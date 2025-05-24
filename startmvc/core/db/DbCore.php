<?php

namespace startmvc\core\db;

use Closure;
use PDO;
use PDOException;
use startmvc\core\Exception;
use startmvc\core\Config;
use startmvc\core\Logger;
use startmvc\core\db\DbCache;

/**
 * Dbcore - 实用的查询构建器和PDO类
 *
 * 数据查询的默认返回类型为关联数组(PDO::FETCH_ASSOC)。
 * 如果需要返回对象，可以在查询方法中指定类型为'object'。
 *
 * @package  Pdox
 */
class DbCore implements DbInterface
{
    /**
     * PDOx 版本
     *
     * @var string
     */
    const VERSION = '1.6.0';

    /**
     * @var PDO|null PDO实例
     */
    public $pdo = null;
    
    /**
     * @var mixed WordPress $wpdb instance
     */
    public $wpdb = null; // THIS LINE MUST BE PRESENT

    /**
     * @var mixed 查询变量
     */
    protected $select = '*';
    protected $from = null;
    protected $where = null;
    protected $limit = null;
    protected $offset = null;
    protected $join = null;
    protected $orderBy = null;
    protected $groupBy = null;
    protected $having = null;
    protected $grouped = false;
    protected $numRows = 0;
    protected $insertId = null;
    protected $query = null;
    protected $error = null;
    protected $result = [];
    protected $prefix = null;

    /**
     * @var array SQL运算符
     */
    protected $operators = ['=', '!=', '<', '>', '<=', '>=', '<>'];

    /**
     * @var Cache|null 缓存实例
     */
    protected $cache = null;

    /**
     * @var string|null 缓存目录
     */
    protected $cacheDir = null;

    /**
     * @var int 查询总数
     */
    protected $queryCount = 0;

    /**
     * @var bool 调试模式
     */
    protected $debug = true;

    /**
     * @var int 事务总数
     */
    protected $transactionCount = 0;

    /**
     * 子节点查询配置
     * @var array
     */
    protected $joinNodes = [];

    // 存储临时更新数据，用于getSql()方法
    protected $_updateData = [];
    
    // 存储临时插入数据，用于getSql()方法
    protected $_insertData = [];
    
    // 存储最后构建的查询
    protected $_lastQuery = '';
    
    // 存储查询类型
    protected $_queryType = '';

    // 设置返回 SQL 标志
    protected $_returnSql = false;

    /**
     * @var array SQL查询日志
     */
    protected static $sqlLogs = [];

    /**
     * 单例实例
     * @var DbCore
     */
    protected static $instance;
    
    /**
     * 是否已连接
     * @var bool
     */
    protected $connected = false;

    /**
     * 数据库配置
     * @var array
     */
    protected $config;

    /**
     * 构造函数
     * @param array|string $config 数据库配置 or 'wordpress' string
     */
    public function __construct($config)
    {
        if ($config === 'wordpress') {
            global $wpdb;
            if (!isset($wpdb) || !is_object($wpdb) || !method_exists($wpdb, 'get_results')) {
                // Try to re-fetch $wpdb if it wasn't available initially or was not the correct object
                // This can happen depending on when this class is instantiated within WordPress load.
                if (isset($GLOBALS['wpdb']) && is_object($GLOBALS['wpdb']) && method_exists($GLOBALS['wpdb'], 'get_results')) {
                    $wpdb = $GLOBALS['wpdb'];
                } else {
                    throw new \startmvc\core\Exception('WordPress $wpdb global is not available or not a valid WPDB object.');
                }
            }
            $this->wpdb = $wpdb;
            $this->prefix = $this->wpdb->prefix ?? ''; // Use null coalescing for safety
            $this->connected = true; 
            // Bypassing original PDO connection and StartMVC cache dir setup for WordPress
            return; 
        }

        // Original StartMVC constructor logic starts here
        $this->config = $config;
        // Ensure prefix is only set from $config if not in WordPress mode
        if (!($config === 'wordpress')) { // This condition is technically redundant due to the return above, but for clarity
             $this->prefix = $config['prefix'] ?? ''; 
        }
        
        // Initialize cache directory (only for non-WordPress)
        if (!empty($config['cachedir'])) {
            $this->cacheDir = $config['cachedir'];
            if (!file_exists($this->cacheDir)) {
                // Suppress errors for mkdir, check if directory exists afterwards
                if (@mkdir($this->cacheDir, 0755, true) === false && !is_dir($this->cacheDir)) {
                    // Log or handle error: "Failed to create cache directory: {$this->cacheDir}"
                    // For now, let it proceed; caching might fail later.
                }
            }
        }
        
        $this->connect(); // Original call to connect for PDO
    }
    
    /**
     * 获取单例实例
     * @param array|string $config 数据库配置 or 'wordpress' string
     * @return DbCore
     */
    public static function getInstance($config = null)
    {
        if (static::$instance === null) {
            if ($config === 'wordpress') {
                static::$instance = new static('wordpress');
            } elseif ($config === null) { 
                // Non-WordPress: $config is null, load from file
                if (!defined('CONFIG_PATH')) {
                     // Fallback or error for CONFIG_PATH not defined
                     throw new \startmvc\core\Exception('CONFIG_PATH is not defined. Cannot load database configuration for non-WordPress context.');
                }
                $db_config_file = CONFIG_PATH . 'database.php';
                if (!file_exists($db_config_file)) {
                    throw new \startmvc\core\Exception('Database configuration file not found: ' . $db_config_file);
                }
                $db_settings = include $db_config_file; // @include can be used if preferred
                if ($db_settings === false || !is_array($db_settings)) {
                    throw new \startmvc\core\Exception('Failed to load or parse database configuration file: ' . $db_config_file);
                }
                if (!isset($db_settings['driver']) || empty($db_settings['driver']) || !isset($db_settings['connections'][$db_settings['driver']])) {
                    throw new \startmvc\core\Exception('Database configuration is invalid. "driver" or "connections" section missing or malformed in ' . $db_config_file);
                }
                $connection_config = $db_settings['connections'][$db_settings['driver']];
                static::$instance = new static($connection_config);
            } else { 
                // Non-WordPress: $config is an array
                static::$instance = new static($config);
            }
        }
        return static::$instance;
    }

    /**
     * 连接数据库
     * @return PDO|object
     * @throws Exception
     */
    protected function connect()
    {
        if ($this->wpdb) {
            return $this->wpdb; // In WordPress mode, $wpdb is the connection
        }
        if ($this->connected && $this->pdo) {
            return $this->pdo;
        }

        if (empty($this->config) || !is_array($this->config)) {
            throw new Exception('Database configuration is missing or invalid for PDO connection.');
        }
        
        // Check for essential config keys before attempting to connect
        $required_keys = ['driver', 'host', 'port', 'database', 'charset', 'username', 'password'];
        foreach ($required_keys as $key) {
            if (!isset($this->config[$key])) {
                throw new Exception("Database configuration missing required key: {$key}");
            }
        }

        try {
            $dsn = "{$this->config['driver']}:host={$this->config['host']};port={$this->config['port']};dbname={$this->config['database']};charset={$this->config['charset']}";
            $this->pdo = new PDO($dsn, $this->config['username'], $this->config['password'], [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
            ]);
            $this->connected = true;
            return $this->pdo;
        } catch (PDOException $e) {
            throw new Exception('数据库连接失败：' . $e->getMessage());
        }
    }

    /**
     * 获取PDO实例 (or $wpdb in WordPress mode)
     * @return PDO|object
     */
    public function getPdo()
    {
        if ($this->wpdb) {
            return $this->wpdb;
        }
        return $this->connect();
    }

    /**
     * 设置查询的表名
     * 
     * @param $table 表名
     *
     * @return $this
     */
    public function table($table)
    {
        if (is_array($table)) {
            $from = '';
            foreach ($table as $key) {
                $from .= $this->prefix . $key . ', ';
            }
            $this->from = rtrim($from, ', ');
        } else {
            if (strpos($table, ',') > 0) {
                $tables = explode(',', $table);
                foreach ($tables as $key => &$value) {
                    $value = $this->prefix . ltrim($value);
                }
                $this->from = implode(', ', $tables);
            } else {
                $this->from = $this->prefix . $table;
            }
        }

        return $this;
    }

    /**
     * 设置查询的表名（table方法的别名）
     * 
     * @param $table 表名
     *
     * @return $this
     */
    public function from($table)
    {
        return $this->table($table);
    }

    /**
     * 设置SELECT查询的字段
     * 
     * @param array|string $fields 要查询的字段
     *
     * @return $this
     */
    public function select($fields)
    {
        $select = is_array($fields) ? implode(', ', $fields) : $fields;
        $this->optimizeSelect($select);

        return $this;
    }

    /**
     * 获取字段的最大值
     * 
     * @param string      $field 字段名
     * @param string|null $name 结果别名
     *
     * @return $this
     */
    public function max($field, $name = null)
    {
        $column = 'MAX(' . $field . ')' . (!is_null($name) ? ' AS ' . $name : '');
        $this->optimizeSelect($column);

        return $this;
    }

    /**
     * 获取字段的最小值
     * 
     * @param string      $field 字段名
     * @param string|null $name 结果别名
     *
     * @return $this
     */
    public function min($field, $name = null)
    {
        $column = 'MIN(' . $field . ')' . (!is_null($name) ? ' AS ' . $name : '');
        $this->optimizeSelect($column);

        return $this;
    }

    /**
     * 获取字段的总和
     * 
     * @param string      $field 字段名
     * @param string|null $name 结果别名
     *
     * @return $this
     */
    public function sum($field, $name = null)
    {
        $column = 'SUM(' . $field . ')' . (!is_null($name) ? ' AS ' . $name : '');
        $this->optimizeSelect($column);

        return $this;
    }

    /**
     * 获取记录数量
     * 
     * @param string      $field 字段名
     * @param string|null $name 结果别名
     *
     * @return $this
     */
    public function count($field, $name = null)
    {
        $column = 'COUNT(' . $field . ')' . (!is_null($name) ? ' AS ' . $name : '');
        $this->optimizeSelect($column);

        return $this;
    }

    /**
     * 获取字段的平均值
     * 
     * @param string      $field 字段名
     * @param string|null $name 结果别名
     *
     * @return $this
     */
    public function avg($field, $name = null)
    {
        $column = 'AVG(' . $field . ')' . (!is_null($name) ? ' AS ' . $name : '');
        $this->optimizeSelect($column);

        return $this;
    }

    /**
     * 表连接操作
     * 
     * @param string      $table 要连接的表名
     * @param string|null $field1 第一个字段
     * @param string|null $operator 操作符
     * @param string|null $field2 第二个字段
     * @param string      $type 连接类型
     *
     * @return $this
     */
    public function join($table, $field1 = null, $operator = null, $field2 = null, $type = '')
    {
        $on = $field1;
        $table = $this->prefix . $table;

        if (!is_null($operator)) {
            $on = !in_array($operator, $this->operators)
                ? $field1 . ' = ' . $operator . (!is_null($field2) ? ' ' . $field2 : '')
                : $field1 . ' ' . $operator . ' ' . $field2;
        }

        $this->join = (is_null($this->join))
            ? ' ' . $type . 'JOIN' . ' ' . $table . ' ON ' . $on
            : $this->join . ' ' . $type . 'JOIN' . ' ' . $table . ' ON ' . $on;

        return $this;
    }

    /**
     * 内连接
     * 
     * @param string $table 要连接的表名
     * @param string $field1 第一个字段
     * @param string $operator 操作符
     * @param string $field2 第二个字段
     *
     * @return $this
     */
    public function innerJoin($table, $field1, $operator = '', $field2 = '')
    {
        return $this->join($table, $field1, $operator, $field2, 'INNER ');
    }

    /**
     * 左连接
     * 
     * @param string $table 要连接的表名
     * @param string $field1 第一个字段
     * @param string $operator 操作符
     * @param string $field2 第二个字段
     *
     * @return $this
     */
    public function leftJoin($table, $field1, $operator = '', $field2 = '')
    {
        return $this->join($table, $field1, $operator, $field2, 'LEFT ');
    }

    /**
     * 右连接
     * 
     * @param string $table 要连接的表名
     * @param string $field1 第一个字段
     * @param string $operator 操作符
     * @param string $field2 第二个字段
     *
     * @return $this
     */
    public function rightJoin($table, $field1, $operator = '', $field2 = '')
    {
        return $this->join($table, $field1, $operator, $field2, 'RIGHT ');
    }

    /**
     * 完全外连接
     * 
     * @param string $table 要连接的表名
     * @param string $field1 第一个字段
     * @param string $operator 操作符
     * @param string $field2 第二个字段
     *
     * @return $this
     */
    public function fullOuterJoin($table, $field1, $operator = '', $field2 = '')
    {
        return $this->join($table, $field1, $operator, $field2, 'FULL OUTER ');
    }

    /**
     * 左外连接
     * 
     * @param string $table 要连接的表名
     * @param string $field1 第一个字段
     * @param string $operator 操作符
     * @param string $field2 第二个字段
     *
     * @return $this
     */
    public function leftOuterJoin($table, $field1, $operator = '', $field2 = '')
    {
        return $this->join($table, $field1, $operator, $field2, 'LEFT OUTER ');
    }

    /**
     * 右外连接
     * 
     * @param string $table 要连接的表名
     * @param string $field1 第一个字段
     * @param string $operator 操作符
     * @param string $field2 第二个字段
     *
     * @return $this
     */
    public function rightOuterJoin($table, $field1, $operator = '', $field2 = '')
    {
        return $this->join($table, $field1, $operator, $field2, 'RIGHT OUTER ');
    }

    /**
     * WHERE条件查询
     * 
     * @param array|string $where 条件
     * @param string       $operator 操作符
     * @param string       $val 值
     * @param string       $type 类型
     * @param string       $andOr 连接词（AND/OR）
     *
     * @return $this
     */
    public function where($where, $operator = null, $val = null, $type = '', $andOr = 'AND')
    {
        if (is_array($where) && !empty($where)) {
            $_where = [];
            foreach ($where as $column => $data) {
                $_where[] = $type . $column . '=' . $this->escape($data);
            }
            $where = implode(' ' . $andOr . ' ', $_where);
        } else {
            if (is_null($where) || empty($where)) {
                return $this;
            }

            if (is_array($operator)) {
                $params = explode('?', $where);
                $_where = '';
                foreach ($params as $key => $value) {
                    if (!empty($value)) {
                        $_where .= $type . $value . (isset($operator[$key]) ? $this->escape($operator[$key]) : '');
                    }
                }
                $where = $_where;
            } elseif (!in_array($operator, $this->operators) || $operator == false) {
                $where = $type . $where . ' = ' . $this->escape($operator);
            } else {
                $where = $type . $where . ' ' . $operator . ' ' . $this->escape($val);
            }
        }

        if ($this->grouped) {
            $where = '(' . $where;
            $this->grouped = false;
        }

        $this->where = is_null($this->where)
            ? $where
            : $this->where . ' ' . $andOr . ' ' . $where;

        return $this;
    }

    /**
     * OR WHERE条件查询
     * 
     * @param array|string $where 条件
     * @param string|null  $operator 操作符
     * @param string|null  $val 值
     *
     * @return $this
     */
    public function orWhere($where, $operator = null, $val = null)
    {
        return $this->where($where, $operator, $val, '', 'OR');
    }

    /**
     * NOT WHERE条件查询
     * 
     * @param array|string $where 条件
     * @param string|null  $operator 操作符
     * @param string|null  $val 值
     *
     * @return $this
     */
    public function notWhere($where, $operator = null, $val = null)
    {
        return $this->where($where, $operator, $val, 'NOT ', 'AND');
    }

    /**
     * OR NOT WHERE条件查询
     * 
     * @param array|string $where 条件
     * @param string|null  $operator 操作符
     * @param string|null  $val 值
     *
     * @return $this
     */
    public function orNotWhere($where, $operator = null, $val = null)
    {
        return $this->where($where, $operator, $val, 'NOT ', 'OR');
    }

    /**
     * @param string $where
     * @param bool   $not
     *
     * @return $this
     */
    public function whereNull($where, $not = false)
    {
        $where = $where . ' IS ' . ($not ? 'NOT' : '') . ' NULL';
        $this->where = is_null($this->where) ? $where : $this->where . ' ' . 'AND ' . $where;

        return $this;
    }

    /**
     * @param string $where
     *
     * @return $this
     */
    public function whereNotNull($where)
    {
        return $this->whereNull($where, true);
    }

    /**
     * @param Closure $obj
     *
     * @return $this
     */
    public function grouped(Closure $obj)
    {
        $this->grouped = true;
        call_user_func_array($obj, [$this]);
        $this->where .= ')';

        return $this;
    }

    /**
     * IN条件查询
     * 
     * @param string $field 字段名
     * @param array  $keys 值数组
     * @param string $type 类型
     * @param string $andOr 连接词（AND/OR）
     *
     * @return $this
     */
    public function in($field, array $keys, $type = '', $andOr = 'AND')
    {
        if (is_array($keys)) {
            $_keys = [];
            foreach ($keys as $k => $v) {
                $_keys[] = is_numeric($v) ? $v : $this->escape($v);
            }
            $where = $field . ' ' . $type . 'IN (' . implode(', ', $_keys) . ')';

            if ($this->grouped) {
                $where = '(' . $where;
                $this->grouped = false;
            }

            $this->where = is_null($this->where)
                ? $where
                : $this->where . ' ' . $andOr . ' ' . $where;
        }

        return $this;
    }

    /**
     * NOT IN条件查询
     * 
     * @param string $field 字段名
     * @param array  $keys 值数组
     *
     * @return $this
     */
    public function notIn($field, array $keys)
    {
        return $this->in($field, $keys, 'NOT ', 'AND');
    }

    /**
     * OR IN条件查询
     * 
     * @param string $field 字段名
     * @param array  $keys 值数组
     *
     * @return $this
     */
    public function orIn($field, array $keys)
    {
        return $this->in($field, $keys, '', 'OR');
    }

    /**
     * OR NOT IN条件查询
     * 
     * @param string $field 字段名
     * @param array  $keys 值数组
     *
     * @return $this
     */
    public function orNotIn($field, array $keys)
    {
        return $this->in($field, $keys, 'NOT ', 'OR');
    }

    /**
     * FIND_IN_SET条件查询
     * 
     * @param string         $field 字段名
     * @param string|integer $key 查找的值
     * @param string         $type 类型
     * @param string         $andOr 连接词（AND/OR）
     *
     * @return $this
     */
    public function findInSet($field, $key, $type = '', $andOr = 'AND')
    {
        $key = is_numeric($key) ? $key : $this->escape($key);
        $where =  $type . 'FIND_IN_SET (' . $key . ', '.$field.')';

        if ($this->grouped) {
            $where = '(' . $where;
            $this->grouped = false;
        }

        $this->where = is_null($this->where)
            ? $where
            : $this->where . ' ' . $andOr . ' ' . $where;

        return $this;
    }

    /**
     * NOT FIND_IN_SET条件查询
     * 
     * @param string $field 字段名
     * @param string $key 查找的值
     *
     * @return $this
     */
    public function notFindInSet($field, $key)
    {
        return $this->findInSet($field, $key, 'NOT ');
    }

    /**
     * OR FIND_IN_SET条件查询
     * 
     * @param string $field 字段名
     * @param string $key 查找的值
     *
     * @return $this
     */
    public function orFindInSet($field, $key)
    {
        return $this->findInSet($field, $key, '', 'OR');
    }

    /**
     * OR NOT FIND_IN_SET条件查询
     * 
     * @param string $field 字段名
     * @param string $key 查找的值
     *
     * @return $this
     */
    public function orNotFindInSet($field, $key)
    {
        return $this->findInSet($field, $key, 'NOT ', 'OR');
    }

    /**
     * BETWEEN条件查询
     * 
     * @param string     $field 字段名
     * @param string|int $value1 最小值
     * @param string|int $value2 最大值
     * @param string     $type 类型
     * @param string     $andOr 连接词（AND/OR）
     *
     * @return $this
     */
    public function between($field, $value1, $value2, $type = '', $andOr = 'AND')
    {
        $where = '(' . $field . ' ' . $type . 'BETWEEN ' . ($this->escape($value1) . ' AND ' . $this->escape($value2)) . ')';
        if ($this->grouped) {
            $where = '(' . $where;
            $this->grouped = false;
        }

        $this->where = is_null($this->where)
            ? $where
            : $this->where . ' ' . $andOr . ' ' . $where;

        return $this;
    }

    /**
     * NOT BETWEEN条件查询
     * 
     * @param string     $field 字段名
     * @param string|int $value1 最小值
     * @param string|int $value2 最大值
     *
     * @return $this
     */
    public function notBetween($field, $value1, $value2)
    {
        return $this->between($field, $value1, $value2, 'NOT ', 'AND');
    }

    /**
     * OR BETWEEN条件查询
     * 
     * @param string     $field 字段名
     * @param string|int $value1 最小值
     * @param string|int $value2 最大值
     *
     * @return $this
     */
    public function orBetween($field, $value1, $value2)
    {
        return $this->between($field, $value1, $value2, '', 'OR');
    }

    /**
     * OR NOT BETWEEN条件查询
     * 
     * @param string     $field 字段名
     * @param string|int $value1 最小值
     * @param string|int $value2 最大值
     *
     * @return $this
     */
    public function orNotBetween($field, $value1, $value2)
    {
        return $this->between($field, $value1, $value2, 'NOT ', 'OR');
    }

    /**
     * LIKE条件查询
     * 
     * @param string $field 字段名
     * @param string $data 匹配的数据
     * @param string $type 类型
     * @param string $andOr 连接词（AND/OR）
     *
     * @return $this
     */
    public function like($field, $data, $type = '', $andOr = 'AND')
    {
        $like = $this->escape($data);
        $where = $field . ' ' . $type . 'LIKE ' . $like;

        if ($this->grouped) {
            $where = '(' . $where;
            $this->grouped = false;
        }

        $this->where = is_null($this->where)
            ? $where
            : $this->where . ' ' . $andOr . ' ' . $where;

        return $this;
    }

    /**
     * OR LIKE条件查询
     * 
     * @param string $field 字段名
     * @param string $data 匹配的数据
     *
     * @return $this
     */
    public function orLike($field, $data)
    {
        return $this->like($field, $data, '', 'OR');
    }

    /**
     * NOT LIKE条件查询
     * 
     * @param string $field 字段名
     * @param string $data 匹配的数据
     *
     * @return $this
     */
    public function notLike($field, $data)
    {
        return $this->like($field, $data, 'NOT ', 'AND');
    }

    /**
     * OR NOT LIKE条件查询
     * 
     * @param string $field 字段名
     * @param string $data 匹配的数据
     *
     * @return $this
     */
    public function orNotLike($field, $data)
    {
        return $this->like($field, $data, 'NOT ', 'OR');
    }

    /**
     * 设置查询结果的LIMIT
     * 
     * @param int      $limit 限制数量
     * @param int|null $limitEnd 结束位置
     *
     * @return $this
     */
    public function limit($limit, $limitEnd = null)
    {
        $this->limit = !is_null($limitEnd)
            ? $limit . ', ' . $limitEnd
            : $limit;

        return $this;
    }

    /**
     * 设置查询结果的OFFSET
     * 
     * @param int $offset 偏移量
     *
     * @return $this
     */
    public function offset($offset)
    {
        $this->offset = $offset;

        return $this;
    }

    /**
     * 设置分页
     * 
     * @param int $perPage 每页记录数
     * @param int $page 页码
     *
     * @return $this
     */
    public function page($perPage, $page)
    {
        $this->limit = $perPage;
        $this->offset = (($page > 0 ? $page : 1) - 1) * $perPage;

        return $this;
    }

    /**
     * 设置查询结果的分组
     * 
     * @param string|array $groupBy 分组字段
     *
     * @return $this
     */
    public function group($groupBy)
    {
        if (is_array($groupBy)) {
            $this->groupBy = implode(', ', $groupBy);
        } else {
            $this->groupBy = $groupBy;
        }
        return $this;
    }

    /**
     * 设置HAVING条件
     * 
     * @param string            $field 字段名
     * @param string|array|null $operator 操作符
     * @param string|null       $val 值
     *
     * @return $this
     */
    public function having($field, $operator = null, $val = null)
    {
        if (is_array($operator)) {
            $fields = explode('?', $field);
            $where = '';
            foreach ($fields as $key => $value) {
                if (!empty($value)) {
                    $where .= $value . (isset($operator[$key]) ? $this->escape($operator[$key]) : '');
                }
            }
            $this->having = $where;
        } elseif (!in_array($operator, $this->operators)) {
            $this->having = $field . ' > ' . $this->escape($operator);
        } else {
            $this->having = $field . ' ' . $operator . ' ' . $this->escape($val);
        }

        return $this;
    }

    /**
     * 获取影响的行数
     *
     * @return int
     */
    public function numRows()
    {
        return $this->numRows;
    }

    /**
     * 获取最后插入的ID
     *
     * @return int|null
     */
    public function insertId()
    {
        return $this->insertId;
    }

    /**
     * 显示错误信息
     * 
     * @throw PDOException
     */
    public function error()
    {
        if ($this->debug === true) {
            if ($this->wpdb && method_exists($this->wpdb, 'print_error')) {
                // $this->wpdb->print_error(); // This prints directly, might not be ideal.
                // Capture $this->wpdb->last_error if not already in $this->error
                if (empty($this->error) && !empty($this->wpdb->last_error)) {
                    $this->error = $this->wpdb->last_error;
                }
            }
            $error_message = "Query: " . htmlspecialchars($this->query ?? '') . "\nError: " . htmlspecialchars($this->error ?? '');
            if (php_sapi_name() === 'cli') {
                die($error_message . PHP_EOL);
            }

            $msg = '<h1>Database Error</h1>';
            $msg .= '<h4>Query: <em style="font-weight:normal;">"' . htmlspecialchars($this->query ?? 'N/A') . '"</em></h4>';
            $msg .= '<h4>Error: <em style="font-weight:normal;">' . htmlspecialchars($this->error ?? 'Unknown error') . '</em></h4>';
            if ($this->wpdb && $this->debug && !empty($this->wpdb->last_error)) {
                 $msg .= '<h4>WPDB Last Error: <em style="font-weight:normal;">' . htmlspecialchars($this->wpdb->last_error) . '</em></h4>';
            }
            die($msg);
        }
        $exception_message = ($this->error ?? 'Unknown database error') . '. (' . ($this->query ?? 'N/A') . ')';
        if ($this->wpdb) {
             // For WordPress, avoid throwing PDOException if it's a WPDB error.
             // Throw a generic exception or a custom one.
             throw new Exception($exception_message);
        } else {
             throw new PDOException($exception_message);
        }
    }

    /**
     * 获取单条记录
     * 
     * @param bool|string $returnSql 是否仅返回SQL或返回类型
     * @param string $argument 参数（当$returnSql指定为类名时使用）
     *
     * @return mixed 返回单条记录
     */
    public function get($returnSql = null, $argument = null)
    {
        $this->limit(1);
        $query = $this->buildSelectQuery();

        // 存储查询，用于getSql方法
        $this->_lastQuery = $query;
        $this->_queryType = 'select';
        
        if ($returnSql === true || $this->_returnSql) {
            $this->_returnSql = false;
            $this->reset();
            return $query;
        }
        
        $result = $this->query($query, false, $returnSql, $argument);
        
        $this->reset();
        return $result;
    }

    /**
     * 获取多条记录
     * 
     * @param bool|string $returnSql 是否仅返回SQL或返回类型
     * @param string $argument 参数（当$returnSql指定为类名时使用）
     *
     * @return mixed 返回多条记录
     */
    public function getAll($returnSql = null, $argument = null)
    {
        $query = $this->buildSelectQuery();
        
        // 存储查询，用于getSql方法
        $this->_lastQuery = $query;
        $this->_queryType = 'select';
        
        if ($returnSql === true || $this->_returnSql) {
            $this->_returnSql = false;
            $this->reset();
            return $query;
        }
        
        $result = $this->query($query, true, $returnSql, $argument);
        
        $this->reset();
        return $result;
    }

    /**
     * 构建SELECT查询SQL
     * 
     * @return string 构建好的SQL语句
     */
    protected function buildSelectQuery()
    {
        $query = 'SELECT ' . $this->select . ' FROM ' . $this->from;

        if (!is_null($this->join)) {
            $query .= $this->join;
        }

        if (!is_null($this->where)) {
            $query .= ' WHERE ' . $this->where;
        }

        if (!is_null($this->groupBy)) {
            $query .= ' GROUP BY ' . $this->groupBy;
        }

        if (!is_null($this->having)) {
            $query .= ' HAVING ' . $this->having;
        }

        if (!is_null($this->orderBy)) {
            $query .= ' ORDER BY ' . $this->orderBy;
        }

        if (!is_null($this->limit)) {
            $query .= ' LIMIT ' . $this->limit;
        }

        if (!is_null($this->offset)) {
            $query .= ' OFFSET ' . $this->offset;
        }

        return $query;
    }

    /**
     * 插入数据
     * 
     * @param array $data 要插入的数据
     * @param bool|string $returnSql 是否仅返回SQL或返回类型
     * @param string $type 插入类型：INSERT, INSERT IGNORE, REPLACE, DUPLICATE
     *
     * @return bool|string|int|null|$this
     */
    public function insert(array $data, $returnSql = false, $type = 'INSERT')
    {
        $query = $this->buildInsertQuery($data, $type);
        
        // 存储插入数据和查询，用于getSql方法
        $this->_insertData = $data;
        $this->_lastQuery = $query;
        $this->_queryType = strtolower(explode(' ', $type)[0]); // insert, replace, etc.

        if ($returnSql === true || $this->_returnSql) {
            $this->_returnSql = false;
            $this->reset(); // Reset before returning SQL
            return $query;
        }

        if ($this->wpdb) {
            $result = $this->query($query, false); // query() handles $wpdb logic
            if ($result !== false) { // $wpdb->query returns number of affected rows or false on error
                $this->insertId = $this->wpdb->insert_id;
                return $this->insertId();
            }
            return false;
        } else {
            if ($this->query($query, false)) { // Original PDO path
                if ($this->pdo) { // Ensure pdo object exists
                    $this->insertId = $this->pdo->lastInsertId();
                    return $this->insertId();
                }
                return false; // Should not happen if query was successful
            }
            return false;
        }
    }

    /**
     * 构建INSERT查询SQL
     * 
     * @param array $data 要插入的数据
     * @param string $type 插入类型：INSERT, INSERT IGNORE, REPLACE, DUPLICATE
     * @return string 构建好的SQL语句
     */
    protected function buildInsertQuery(array $data, $type = 'INSERT')
    {
        // 标准化插入类型，默认为标准INSERT
        $type = strtoupper($type);
        
        // 根据类型设置SQL前缀
        switch ($type) {
            case 'INSERT IGNORE':
            case 'IGNORE':
                $query = 'INSERT IGNORE INTO ' . $this->from;
                break;
            case 'INSERT OR IGNORE':
                $query = 'INSERT OR IGNORE INTO ' . $this->from;
                break;
            case 'REPLACE':
                $query = 'REPLACE INTO ' . $this->from;
                break;
            default:
        $query = 'INSERT INTO ' . $this->from;
                break;
        }

        $values = array_values($data);
        if (isset($values[0]) && is_array($values[0])) {
            $column = implode(', ', array_keys($values[0]));
            $query .= ' (' . $column . ') VALUES ';
            foreach ($values as $value) {
                $val = implode(', ', array_map([$this, 'escape'], $value));
                $query .= '(' . $val . '), ';
            }
            $query = trim($query, ', ');
            
            // 处理ON DUPLICATE KEY UPDATE
            if ($type === 'DUPLICATE') {
                $query .= ' ON DUPLICATE KEY UPDATE ';
                $updates = [];
                foreach (array_keys($values[0]) as $column) {
                    $updates[] = "$column = VALUES($column)";
                }
                $query .= implode(', ', $updates);
            }
        } else {
            $column = implode(', ', array_keys($data));
            $val = implode(', ', array_map([$this, 'escape'], $data));
            $query .= ' (' . $column . ') VALUES (' . $val . ')';
            
            // 处理ON DUPLICATE KEY UPDATE
            if ($type === 'DUPLICATE') {
                $query .= ' ON DUPLICATE KEY UPDATE ';
                $updates = [];
                foreach (array_keys($data) as $column) {
                    $updates[] = "$column = VALUES($column)";
                }
                $query .= implode(', ', $updates);
            }
        }

            return $query;
        }

    /**
     * 更新数据
     * 
     * @param array $data 要更新的数据
     * @param bool  $returnSql 是否仅返回SQL，而不执行
     *
     * @return mixed|string|$this
     */
    public function update(array $data, $returnSql = false)
    {
        $query = $this->buildUpdateQuery($data);
        
        // 存储更新数据和查询，用于getSql方法
        $this->_updateData = $data;
        $this->_lastQuery = $query;
        $this->_queryType = 'update';
        
        if ($returnSql === true || $this->_returnSql) {
            $this->_returnSql = false;
            $this->reset();
            return $query;
        }
        
        return $this->query($query, false);
    }

    /**
     * 构建UPDATE查询SQL
     * 
     * @param array $data 要更新的数据
     * @return string 构建好的SQL语句
     */
    protected function buildUpdateQuery(array $data)
    {
        $query = 'UPDATE ' . $this->from . ' SET ';
        $values = [];

        foreach ($data as $column => $val) {
            $values[] = $column . '=' . $this->escape($val);
        }
        $query .= implode(',', $values);

        if (!is_null($this->where)) {
            $query .= ' WHERE ' . $this->where;
        }

        if (!is_null($this->orderBy)) {
            $query .= ' ORDER BY ' . $this->orderBy;
        }

        if (!is_null($this->limit)) {
            $query .= ' LIMIT ' . $this->limit;
        }

        return $query;
    }

    /**
     * 删除数据
     * 
     * @param bool $returnSql 是否仅返回SQL，而不执行
     *
     * @return mixed|string|$this
     */
    public function delete($returnSql = false)
    {
        $query = $this->buildDeleteQuery();
        
        // 存储查询，用于getSql方法
        $this->_lastQuery = $query;
        $this->_queryType = 'delete';
        
        if ($returnSql === true || $this->_returnSql) {
            $this->_returnSql = false;
            $this->reset();
            return $query;
        }
        
        return $this->query($query, false);
    }

    /**
     * 构建DELETE查询SQL
     * 
     * @return string 构建好的SQL语句
     */
    protected function buildDeleteQuery()
    {
        $query = 'DELETE FROM ' . $this->from;

        if (!is_null($this->where)) {
            $query .= ' WHERE ' . $this->where;
        }

        if (!is_null($this->orderBy)) {
            $query .= ' ORDER BY ' . $this->orderBy;
        }

        if (!is_null($this->limit)) {
            $query .= ' LIMIT ' . $this->limit;
        }

        if ($query === 'DELETE FROM ' . $this->from) {
            $query = 'TRUNCATE TABLE ' . $this->from;
        }

        return $query;
    }

    /**
     * 获取当前构建的SQL语句而不执行
     * 
     * @return $this
     */
    public function getSql()
    {
        $this->_returnSql = true;
        return $this;
    }

    /**
     * 分析表
     *
     * @return mixed
     */
    public function analyze()
    {
        return $this->query('ANALYZE TABLE ' . $this->from, false);
    }

    /**
     * 检查表
     *
     * @return mixed
     */
    public function check()
    {
        return $this->query('CHECK TABLE ' . $this->from, false);
    }

    /**
     * 校验表
     *
     * @return mixed
     */
    public function checksum()
    {
        return $this->query('CHECKSUM TABLE ' . $this->from, false);
    }

    /**
     * 优化表
     *
     * @return mixed
     */
    public function optimize()
    {
        return $this->query('OPTIMIZE TABLE ' . $this->from, false);
    }

    /**
     * 修复表
     *
     * @return mixed
     */
    public function repair()
    {
        return $this->query('REPAIR TABLE ' . $this->from, false);
    }

    /**
     * 清空表数据
     *
     * @return mixed
     */
    public function truncate()
    {
        return $this->query('TRUNCATE TABLE ' . $this->from, false);
    }

    /**
     * 删除表
     *
     * @return mixed
     */
    public function drop()
    {
        return $this->query('DROP TABLE ' . $this->from, false);
    }

    /**
     * 开始事务
     *
     * @return bool
     */
    public function transaction()
    {
        if ($this->wpdb) {
            // $wpdb doesn't support nested transactions or savepoints directly like PDO.
            // We'll implement basic, single-level transaction support.
            if ($this->transactionCount === 0) {
                $this->wpdb->query('START TRANSACTION');
            }
            $this->transactionCount++;
            return true; // Or perhaps return the result of the query.
        } else {
            if (!$this->transactionCount++) {
                return $this->pdo->beginTransaction();
            }
            $this->pdo->exec('SAVEPOINT trans' . $this->transactionCount);
            return $this->transactionCount >= 0;
        }
    }

    /**
     * 提交事务
     *
     * @return bool
     */
    public function commit()
    {
        if ($this->wpdb) {
            if ($this->transactionCount > 0) {
                $this->transactionCount--;
                if ($this->transactionCount === 0) {
                    return $this->wpdb->query('COMMIT');
                }
            }
            return true; // Or based on query result
        } else {
            if (!--$this->transactionCount) {
                if ($this->pdo) {
                    return $this->pdo->commit();
                }
                return false; // Should not happen if pdo is not available
            }
            return $this->transactionCount >= 0;
        }
    }

    /**
     * 回滚事务
     *
     * @return bool
     */
    public function rollBack()
    {
        if ($this->wpdb) {
            if ($this->transactionCount > 0) {
                $this->transactionCount--;
                if ($this->transactionCount === 0 || $this->wpdb->last_error) { // Also rollback if an error occurred
                    $this->wpdb->query('ROLLBACK');
                }
            }
             return true; // Or based on query result
        } else {
            if (! $this->pdo) return false; // No PDO object
            if (--$this->transactionCount) {
                $this->pdo->exec('ROLLBACK TO trans' . ($this->transactionCount + 1));
                return true;
            }
            return $this->pdo->rollBack();
        }
    }

    /**
     * 执行SQL语句
     *
     * @return mixed
     */
    public function exec()
    {
        if (is_null($this->query)) {
            return null;
        }

        if ($this->wpdb) {
            $result = $this->wpdb->query($this->query);
            if ($result === false && !empty($this->wpdb->last_error)) {
                $this->error = $this->wpdb->last_error;
                $this->error(); // Trigger error handling
            }
            return $result; // Number of affected rows or false
        } else {
            if (!$this->pdo) return false; // No PDO object
            $query = $this->pdo->exec($this->query);
            if ($query === false) {
                $this->error = $this->pdo->errorInfo()[2];
                $this->error();
            }
            return $query;
        }
    }

    /**
     * 获取查询结果
     * 
     * @param string $type 返回类型
     * @param string $argument 参数
     * @param bool   $all 是否获取所有结果
     *
     * @return mixed
     */
    public function fetch($type = null, $argument = null, $all = false)
    {
        if (is_null($this->query)) {
            return null;
        }

        if ($this->wpdb) {
            // This method is more for PDO style.
            // The main query() method already handles $wpdb->get_results()
            // For direct $wpdb fetching if needed, it would be similar to query()
            // but this method is unlikely to be called directly in WP mode if query() is used.
            // If it were, it would need its own $wpdb->get_results logic.
            // For now, assume query() handles WP fetching.
            // If called, it implies a misuse or needs specific WP implementation here.
            $this->error = "fetch() method is not directly supported in WordPress mode; use get() or getAll().";
            $this->error();
            return null;
        }

        if (!$this->pdo) {
             $this->error = "PDO object not available for fetch().";
             $this->error();
             return null;
        }

        $stmt = $this->pdo->query($this->query);
        if (!$stmt) {
            $this->error = $this->pdo->errorInfo()[2];
            $this->error();
            return null; // Return null on error
        }

        $fetch_style = $this->getFetchType($type);
        if ($fetch_style === PDO::FETCH_CLASS && $argument !== null) {
            $stmt->setFetchMode($fetch_style, $argument);
        } else {
            $stmt->setFetchMode($fetch_style);
        }
        
        $result = $all ? $stmt->fetchAll() : $stmt->fetch();
        $this->numRows = ($stmt->rowCount() > 0) ? $stmt->rowCount() : (is_array($result) ? count($result) : ($result ? 1 : 0));
        return $result;
    }

    /**
     * 获取所有查询结果
     * 
     * @param string $type 返回类型
     * @param string $argument 参数
     *
     * @return mixed
     */
    public function fetchAll($type = null, $argument = null)
    {
        return $this->fetch($type, $argument, true);
    }

    /**
     * 执行SQL查询
     * 
     * @param string     $query SQL查询语句
     * @param array|bool $all 是否获取所有结果
     * @param string     $type 返回类型
     * @param string     $argument 参数
     *
     * @return $this|mixed
     */
    public function query($query, $all = true, $type = null, $argument = null)
    {
        $this->reset();
        $startTime = microtime(true);
        $params_for_log = []; // For logging with parameters

        // WordPress Mode
        if ($this->wpdb) {
            // If $all is an array, it means parameters are passed for prepared statement (though $wpdb uses sprintf/prepare)
            // This part is tricky because the original class uses ? for placeholders and $wpdb->prepare uses %s, %d, %f.
            // For simplicity, we'll assume the query string is already prepared if it's a direct call to query() in WP mode.
            // If you need to support `Db::query("SELECT * FROM users WHERE id = ?", [$id])` in WP,
            // it would require a more complex parsing and conversion to $wpdb->prepare format.
            // The existing builder methods (where, select, etc.) should construct the query string directly.
            if (is_array($all)) {
                // This specific parameter binding style is more PDO-like.
                // For $wpdb, one typically uses $wpdb->prepare().
                // We will log these params, but assume $query is mostly pre-built by other methods.
                $params_for_log = $all;
                // The original code had logic to replace '?' with escaped params here.
                // Replicating that accurately for $wpdb without $wpdb->prepare is complex.
                // Let's assume $query is mostly complete or uses $wpdb specific placeholders if prepared externally.
                // For now, we'll just use the $query as is for $wpdb.
                 $this->query = $query; // Use the query directly
            } else {
                $this->query = preg_replace('/\s\s+|\t\t+/', ' ', trim($query));
            }

            $query_lower = strtolower(trim($this->query));
            $query_type = '';

            if (strpos($query_lower, 'select') === 0) $query_type = 'select';
            else if (strpos($query_lower, 'insert') === 0) $query_type = 'insert';
            else if (strpos($query_lower, 'update') === 0) $query_type = 'update';
            else if (strpos($query_lower, 'delete') === 0) $query_type = 'delete';
            else if (strpos($query_lower, 'show') === 0) $query_type = 'show'; // e.g. SHOW TABLES
            else $query_type = 'other'; // Analyze, optimize, truncate etc.

            // Disable StartMVC's file cache when in WordPress mode, $wpdb has its own.
            $this->cache = null;

            if ($query_type === 'select' || $query_type === 'show') {
                $wpOutputType = ARRAY_A; // Default
                $pdoFetchStyle = $this->getFetchType($type);

                if ($pdoFetchStyle === PDO::FETCH_OBJ) {
                    $wpOutputType = OBJECT;
                } elseif ($pdoFetchStyle === PDO::FETCH_CLASS) {
                    // $wpdb->get_results can return objects, but not directly instances of a specific class with constructor args.
                    // We fetch as OBJECT or ARRAY_A and then manually create instances if $argument (classname) is provided.
                    $wpOutputType = OBJECT; // Fetch as generic objects first
                }
                
                if ($all) { // Corresponds to getAll()
                    $this->result = $this->wpdb->get_results($this->query, $wpOutputType);
                } else { // Corresponds to get() - expecting a single row
                    $this->result = $this->wpdb->get_row($this->query, $wpOutputType);
                }
                
                $this->numRows = $this->wpdb->num_rows;

                if ($pdoFetchStyle === PDO::FETCH_CLASS && $argument !== null && !empty($this->result)) {
                    if (class_exists($argument)) {
                        $hydratedResult = [];
                        $results_to_hydrate = is_array($this->result) ? $this->result : [$this->result];
                        foreach ($results_to_hydrate as $row) {
                            if($row === null) continue;
                            $instance = new $argument();
                            foreach ($row as $key => $value) {
                                $instance->$key = $value;
                            }
                            $hydratedResult[] = $instance;
                        }
                        $this->result = $all ? $hydratedResult : ($hydratedResult[0] ?? null);
                    } else {
                        // Class not found, log or handle error, return raw result
                        // For now, returning the raw $wpOutputType result
                    }
                }

            } else { // INSERT, UPDATE, DELETE, other
                $exec_result = $this->wpdb->query($this->query);
                if ($exec_result === false) {
                    $this->error = $this->wpdb->last_error;
                    if (!empty($this->error)) $this->error(); // Trigger error handling only if there's an error message
                    $this->result = false; // Ensure result is explicitly false on error
                } else {
                    $this->result = $exec_result; // Number of affected rows
                    if ($query_type === 'insert') {
                        // $this->insertId is set in the insert() method.
                    }
                    $this->numRows = is_numeric($exec_result) ? $exec_result : 0;
                }
            }
            
            if (!empty($this->wpdb->last_error) && empty($this->error)) { // Check if error was set by $this->error() already
                $this->error = $this->wpdb->last_error;
                // Potentially call $this->error() again if it wasn't triggered for some reason
            }

            // Node parsing - this was specific to the original structure, might need review with $wpdb
            $currentJoinNodes = $this->joinNodes;
            if (!empty($currentJoinNodes) && is_array($this->result)) {
                 $this->result = $this->nodeParser($this->result);
            }

        } else { // Original PDO Logic
            if (!$this->pdo) {
                 throw new Exception("PDO connection not available.");
            }
            if (is_array($all) || func_num_args() === 1 && !is_bool($all)) {
                // This is the path for Db::query("SELECT * FROM foo WHERE id = ?", [$id]);
                $params_for_log = is_array($all) ? $all : [];
                // The original code built the query by replacing '?'
                // Modern PDO usage would use prepared statements and execute.
                // For now, sticking to the original's direct replacement logic for this specific case.
                $parts = explode('?', $query);
                $newQuery = '';
                foreach ($parts as $key => $value) {
                    if (!empty($value)) {
                        $newQuery .= $value . (isset($params_for_log[$key]) ? $this->escape($params_for_log[$key]) : '');
                    }
                }
                $this->query = $newQuery;
                // This path in original code returned $this, not executing the query.
                // This seems like a way to build a query with params, then call exec() or fetch() later.
                // However, exec() and fetch() in original code don't take $params.
                // This path is confusing. Let's assume it's for query building only.
                // To make it runnable, it would need to execute here.
                // For now, to match original return type for this branch:
                 $executionTime = microtime(true) - $startTime;
                 self::logSql($this->query, $params_for_log, $executionTime);
                 return $this; // Original behavior for this specific argument pattern
            }

            $this->query = preg_replace('/\s\s+|\t\t+/', ' ', trim($query));
            $is_select_like = false;
            foreach (['select', 'optimize', 'check', 'repair', 'checksum', 'analyze', 'show'] as $value) {
                if (stripos($this->query, $value) === 0) {
                    $is_select_like = true;
                    break;
                }
            }

            $fetch_style = $this->getFetchType($type);
            $cached_result = false;

            if ($this->cache !== null && $fetch_style !== PDO::FETCH_CLASS && $is_select_like) {
                $cached_result = $this->cache->getCache($this->query, true);
            }

            if ($cached_result !== false) {
                $this->result = $cached_result;
                $this->numRows = is_array($this->result) ? count($this->result) : ($this->result === '' || $this->result === null ? 0 : 1);
                $currentJoinNodes = $this->joinNodes;
                if (!empty($currentJoinNodes) && is_array($this->result)) {
                    $this->result = $this->nodeParser($this->result);
                }
            } elseif ($is_select_like) {
                $stmt = $this->pdo->query($this->query);
                if ($stmt) {
                    $this->numRows = $stmt->rowCount();
                    if ($this->numRows > 0) {
                        if ($fetch_style === PDO::FETCH_CLASS && $argument !== null) {
                            $stmt->setFetchMode($fetch_style, $argument);
                        } else {
                            $stmt->setFetchMode($fetch_style);
                        }
                        $this->result = $all ? $stmt->fetchAll() : $stmt->fetch();
                        
                        $currentJoinNodes = $this->joinNodes;
                        if (!empty($currentJoinNodes) && is_array($this->result)) {
                            $this->result = $this->nodeParser($this->result);
                        }
                    } else {
                        $this->result = $all ? [] : null; // Ensure consistent empty result
                    }
                    if ($this->cache !== null && $fetch_style !== PDO::FETCH_CLASS) {
                        $this->cache->setCache($this->query, $this->result);
                    }
                } else {
                    $this->error = $this->pdo->errorInfo()[2];
                    $this->error();
                }
            } else { // Not a SELECT-like query, and not cached (or cache disabled)
                $this->result = $this->pdo->exec($this->query);
                if ($this->result === false) {
                    $this->error = $this->pdo->errorInfo()[2];
                    $this->error();
                }
                $this->numRows = is_numeric($this->result) ? $this->result : 0;
            }
            $this->cache = null; // Reset cache instance after use
        }

        $executionTime = microtime(true) - $startTime;
        self::logSql($this->query, $params_for_log, $executionTime);

        $this->queryCount++;
        return $this->result;
    }

    /**
     * 转义字符串
     * 
     * @param $data 要转义的数据
     *
     * @return string
     */
    public function escape($data)
    {
        if ($data === null) {
            return 'NULL';
        }
        if (is_int($data) || is_float($data)) {
            // Ensure float is formatted correctly for SQL (no locale specific comma)
            if (is_float($data)) {
                 return rtrim(rtrim(number_format($data, 10, '.', ''), '0'), '.');
            }
            return $data;
        }
        if ($this->wpdb) {
            // $wpdb->prepare uses %s for strings, which handles escaping.
            // For direct value escaping, _real_escape is available but typically not used directly in queries.
            // $wpdb->quote() is not a standard method.
            // The most common way is to use $wpdb->prepare.
            // If building queries manually and needing to escape, this is how:
            return "'" . $this->wpdb->_real_escape((string)$data) . "'";
        }
        if ($this->pdo) {
            return $this->pdo->quote((string)$data);
        }
        // Fallback if no DB connection active, though this shouldn't happen in normal flow
        return "'" . addslashes((string)$data) . "'"; // Basic fallback, not recommended for production
    }

    /**
     * 设置缓存
     * 
     * @param int|null $time 缓存时间（秒），null表示使用默认配置
     *
     * @return $this
     */
    public function cache($time = null)
    {
        // 如果未指定缓存时间，则使用配置中的默认值
        if ($time === null) {
            // 优先使用数据库配置中的cacheTime
            if (!empty($this->config['cachetime'])) {
                $time = $this->config['cachetime'];
            } else {
                // 如果数据库配置中没有设置，使用缓存配置中的defaultTime
                $cacheConfig = config('cache');
                $time = $cacheConfig['file']['cacheTime'] ?? 3600; // 默认1小时
            }
        }
        
        // 优先使用数据库配置中的cachedir
        if (!empty($this->config['cachedir'])) {
            $cacheDir = $this->config['cachedir'];
        } else {
            // 如果数据库配置中没有设置，则使用缓存配置
            $cacheConfig = config('cache');
            $cacheDir = CACHE_PATH . ($cacheConfig['file']['cacheDir'] ?? 'db/');
        }
        
        // 确保缓存目录存在
        if (!file_exists($cacheDir)) {
            mkdir($cacheDir, 0755, true);
        }
        
        // 使用DbCache类创建缓存实例
        $this->cache = new DbCache($cacheDir, $time);

        return $this;
    }

    /**
     * 获取查询次数
     *
     * @return int
     */
    public function queryCount()
    {
        return $this->queryCount;
    }

    /**
     * 获取当前查询语句
     *
     * @return string|null
     */
    public function getQuery()
    {
        return $this->query;
    }

    /**
     * 析构函数，释放PDO实例
     *
     * @return void
     */
    public function __destruct()
    {
        $this->pdo = null;
        // $this->wpdb is global, not managed by this class instance lifecycle for nulling
    }

    /**
     * 重置查询参数
     *
     * @return void
     */
    protected function reset()
    {
        $this->select = '*';
        $this->from = null;
        $this->where = null;
        $this->limit = null;
        $this->offset = null;
        $this->orderBy = null;
        $this->groupBy = null;
        $this->having = null;
        $this->join = null;
        $this->grouped = false;
        $this->numRows = 0;
        $this->insertId = null;
        $this->query = null;
        $this->error = null;
        $this->result = [];
        $this->joinNodes = []; // 重置子节点查询配置
        $this->transactionCount = 0;
    }

    /**
     * 获取获取结果的类型
     * 
     * @param  $type 类型
     *
     * @return int
     */
    protected function getFetchType($type)
    {
        return $type === 'class'
            ? PDO::FETCH_CLASS
            : ($type === 'object'
                ? PDO::FETCH_OBJ
                : PDO::FETCH_ASSOC);
    }

    /**
     * 优化选择的字段
     *
     * @param string $fields 字段
     *
     * @return void
     */
    private function optimizeSelect($fields)
    {
        $this->select = $this->select === '*'
            ? $fields
            : $this->select . ', ' . $fields;
    }

    /**
     * 记录SQL查询日志
     *
     * @param string $sql SQL语句
     * @param array $params 绑定参数
     * @param float $executionTime 执行时间（毫秒）
     * @return void
     */
    protected static function logSql($sql, $params = [], $executionTime = 0)
    {
        self::$sqlLogs[] = [
            'sql' => $sql,
            'params' => $params,
            'time' => number_format($executionTime, 2) . 'ms',
            'timestamp' => microtime(true)
        ];
    }
    
    /**
     * 获取SQL日志列表
     *
     * @return array 所有记录的SQL日志
     */
    public static function getSqlLogs()
    {
        return self::$sqlLogs;
    }

    /**
     * 获取第一条记录
     * @return array|object|null
     */
    public function first()
    {
        $this->limit(1);
        $result = $this->get();
        return $result ? $result[0] : null;
    }

    /**
     * 获取单个字段的值
     * @param string $column 字段名
     * @return mixed
     */
    public function value($column)
    {
        $this->select($column);
        $this->limit(1);
        $result = $this->get();
        if ($result && isset($result[0])) {
            return $result[0]->$column ?? null;
        }
        return null;
    }

    /**
     * 获取指定列的所有值
     * @param string $column 要获取的字段名
     * @param string|null $key 作为返回数组索引的字段名
     * @return array
     */
    public function column($column, $key = null)
    {
        if (!is_null($key)) {
            // 如果提供了$key参数，选择两个字段并构建关联数组
            $this->select(implode(', ', [$key, $column]));
            $result = $this->get();
            
            if (is_array($result)) {
                // 使用array_column构建键值对数组
                return array_column($result, $column, $key);
            }
            
            return $result;
        } else {
            // 如果只提供了$column参数，直接使用PDO::FETCH_COLUMN获取结果
            $this->select($column);
            
            // 重置查询以便直接执行
            $query = $this->buildSelectQuery();
            $this->reset();
            $this->query = $query;
            
            // 直接使用PDO获取列数据
            $stmt = $this->pdo->query($this->query);
            if ($stmt) {
                return $stmt->fetchAll(PDO::FETCH_COLUMN, 0);
            }
            
            return [];
        }
    }

    /**
     * 获取最后执行的SQL语句
     * @param bool $withTime 是否包含执行时间
     * @return string|array 最后执行的SQL语句
     */
    public static function lastQuery($withTime = false)
    {
        $logs = self::getSqlLogs();
        if (empty($logs)) {
            return '';
        }
        
        $last = end($logs);
        
        if ($withTime) {
            return [
                'sql' => $last['sql'],
                'time' => $last['time'],
                'timestamp' => $last['timestamp']
            ];
        }
        
        return $last['sql'];
    }

    /**
     * 布尔值取反（0变1，1变0）
     * 
     * @param string $column 列名
     * @return int|bool 影响的行数或失败时返回false
     */
    public function invert($column)
    {
        $query = "UPDATE {$this->from} SET {$column} = !{$column}";
        
        if (!is_null($this->where)) {
            $query .= ' WHERE ' . $this->where;
        }
        
        // 存储查询，用于getSql方法
        $this->_lastQuery = $query;
        $this->_queryType = 'update';
        
        if ($this->_returnSql) {
            $this->_returnSql = false;
            $this->reset();
            return $query;
        }
        
        return $this->query($query, false);
    }

    /**
     * 列值递增更新
     * 
     * @param string $column 列名
     * @param int $count 递增的数值，默认为1
     * @return int|bool 影响的行数或失败时返回false
     */
    public function inc($column, int $count = 1)
    {
        $query = "UPDATE {$this->from} SET {$column} = {$column} + {$count}";
        
        if (!is_null($this->where)) {
            $query .= ' WHERE ' . $this->where;
        }
        
        // 存储查询，用于getSql方法
        $this->_lastQuery = $query;
        $this->_queryType = 'update';
        
        if ($this->_returnSql) {
            $this->_returnSql = false;
            $this->reset();
            return $query;
        }
        
        return $this->query($query, false);
    }

    /**
     * 列值递减更新
     * 
     * @param string $column 列名
     * @param int $count 递减的数值，默认为1
     * @return int|bool 影响的行数或失败时返回false
     */
    public function dec($column, int $count = 1)
    {
        $query = "UPDATE {$this->from} SET {$column} = {$column} - {$count}";
        
        if (!is_null($this->where)) {
            $query .= ' WHERE ' . $this->where;
        }
        
        // 存储查询，用于getSql方法
        $this->_lastQuery = $query;
        $this->_queryType = 'update';
        
        if ($this->_returnSql) {
            $this->_returnSql = false;
            $this->reset();
            return $query;
        }
        
        return $this->query($query, false);
    }

    /**
     * 定义子节点查询
     * 
     * @param string $alias 子节点名称，将作为结果集中的键名
     * @param array $columns 子节点要查询的字段，格式为 ['字段别名' => '表.字段名']
     * @return $this
     */
    public function joinNode($alias, $columns)
    {
        // 检查是否有JOIN语句
        if (is_null($this->join)) {
            return $this;
        }
        
        $this->joinNodes[] = $alias;

        // 构建字段列表
        $fieldList = [];
        foreach ($columns as $alias_col => $field) { // Changed $alias to $alias_col to avoid conflict
            $fieldList[] = "{$field} AS {$alias_col}";
        }

        // 使用子查询构建嵌套数据
        // This subquery is conceptual. Actual implementation depends on DB's JSON or XML capabilities.
        // For MySQL 5.7+, you might use JSON_OBJECT or JSON_ARRAYAGG.
        // Example: (SELECT JSON_ARRAYAGG(JSON_OBJECT('id', o.id, 'amount', o.amount)) FROM orders o WHERE o.user_id = main_table.id)
        // The $this->from and $this->where in the subquery below are likely incorrect as they refer to the main query's state.
        // This part needs significant rework for a robust solution.
        $subQuery = "(SELECT " . implode(', ', $fieldList) . " FROM " . $this->from . " WHERE " . $this->where . ")"; // This subquery logic is flawed
        
        // 将子查询添加到SELECT中
        $this->select("({$subQuery}) AS {$alias}");
        
        // 添加GROUP BY子句 - This also needs careful consideration based on main query structure.
        if (is_null($this->groupBy)) {
            // $this->group($this->from . '.id'); // This is a simplistic assumption
        }
                    
        return $this;
    }

    /**
     * 解析查询结果中的子查询数据
     * 递归处理结果集中的子节点数据
     * 
     * @param mixed $results 查询结果
     * @return mixed 处理后的结果
     */
    protected function nodeParser($results)
    {
        if (empty($this->joinNodes)) {
            return $results;
        }
        
        // This parsing logic assumes that the subquery (from joinNode) returns a JSON string
        // that needs to be decoded. This is highly dependent on how the SQL query is constructed.
        array_walk_recursive($results, function(&$value, $key) {
            if (in_array($key, $this->joinNodes) && is_string($value)) {
                $decoded = json_decode($value, true);
                if (json_last_error() === JSON_ERROR_NONE) {
                    $value = $decoded;
                }
            }
        });
        
        return $results;
    }

    /**
     * 设置排序
     * 
     * @param string|array $columns 排序字段
     * @param string $order 排序方式
     * @return $this
     */
    public function order($columns, $order = 'ASC')
    {
        if (is_array($columns)) {
            $this->orderBy = implode(', ', array_map(function($column) use ($order) {
                return "{$column} {$order}";
            }, $columns));
        } else {
            // 处理特殊情况如RAND()
            if (strtolower($columns) === 'rand()') {
                $this->orderBy = $columns;
            } else if (stristr($columns, ' ')) {
                // 如果已经包含空格，可能已经指定了排序方向
                $this->orderBy = $columns;
            } else {
                $this->orderBy = "{$columns} {$order}";
            }
        }
        return $this;
    }

    /**
     * 判断字段为NULL
     * 
     * @param string|array $column 字段名
     * @return $this
     */
    public function isNull($column)
    {
        if (is_array($column)) {
            foreach ($column as $col) {
                $this->where($col, 'IS NULL');
            }
        } else {
            $this->where($column, 'IS NULL');
        }
        return $this;
    }

    /**
     * OR条件判断字段为NULL
     * 
     * @param string|array $column 字段名
     * @return $this
     */
    public function orIsNull($column)
    {
        if (is_array($column)) {
            foreach ($column as $col) {
                $this->orWhere($col, 'IS NULL');
            }
        } else {
            $this->orWhere($column, 'IS NULL');
        }
        return $this;
    }

    /**
     * 判断字段不为NULL
     * 
     * @param string|array $column 字段名
     * @return $this
     */
    public function notNull($column)
    {
        if (is_array($column)) {
            foreach ($column as $col) {
                $this->where($col, 'IS NOT NULL');
            }
        } else {
            $this->where($column, 'IS NOT NULL');
        }
        return $this;
    }

    /**
     * OR条件判断字段不为NULL
     * 
     * @param string|array $column 字段名
     * @return $this
     */
    public function orNotNull($column)
    {
        if (is_array($column)) {
            foreach ($column as $col) {
                $this->orWhere($col, 'IS NOT NULL');
            }
        } else {
            $this->orWhere($column, 'IS NOT NULL');
        }
        return $this;
    }
}

/**
 * 使用链式操作获取SQL示例：
 * 
 * // SELECT操作：获取查询SQL - 使用getSql()方法（推荐）
 * $sql = Db::table('users')->where('id', 1)->getSql()->get();
 * // 结果: SELECT * FROM users WHERE id = 1 LIMIT 1
 * 
 * // SELECT操作：使用参数方式获取SQL（向后兼容）
 * $sql = Db::table('users')->where('id', 1)->get(true);
 * // 结果: SELECT * FROM users WHERE id = 1 LIMIT 1
 * 
 * // 获取多条记录SQL
 * $sql = Db::table('users')->where('status', 1)->getSql()->getAll();
 * // 结果: SELECT * FROM users WHERE status = 1
 * 
 * // INSERT操作：获取插入SQL - 使用getSql()方法（推荐）
 * $data = ['name' => 'test', 'email' => 'test@example.com'];
 * $sql = Db::table('users')->getSql()->insert($data);
 * // 结果: INSERT INTO users (name, email) VALUES ('test', 'test@example.com')
 * 
 * // INSERT操作：使用参数方式获取SQL（向后兼容）
 * $data = ['name' => 'test', 'email' => 'test@example.com'];
 * $sql = Db::table('users')->insert($data, true);
 * // 结果: INSERT INTO users (name, email) VALUES ('test', 'test@example.com')
 * 
 * // UPDATE操作：获取更新SQL - 使用getSql()方法（推荐）
 * $data = ['name' => 'updated'];
 * $sql = Db::table('users')->where('id', 1)->getSql()->update($data);
 * // 结果: UPDATE users SET name='updated' WHERE id = 1
 * 
 * // UPDATE操作：使用参数方式获取SQL（向后兼容）
 * $data = ['name' => 'updated'];
 * $sql = Db::table('users')->where('id', 1)->update($data, true);
 * // 结果: UPDATE users SET name='updated' WHERE id = 1
 * 
 * // DELETE操作：获取删除SQL - 使用getSql()方法（推荐）
 * $sql = Db::table('users')->where('id', 1)->getSql()->delete();
 * // 结果: DELETE FROM users WHERE id = 1
 * 
 * // DELETE操作：使用参数方式获取SQL（向后兼容）
 * $sql = Db::table('users')->where('id', 1)->delete(true);
 * // 结果: DELETE FROM users WHERE id = 1
 * 
 * // 使用不同返回类型的示例：
 * // 返回关联数组（默认）
 * $result = Db::table('users')->where('id', 1)->get();
 * // $result = ['id' => 1, 'name' => 'test', 'email' => 'test@example.com']
 * 
 * // 返回对象
 * $result = Db::table('users')->where('id', 1)->get('object');
 * // $result->id = 1
 * // $result->name = 'test'
 * 
 * // 特殊更新操作示例：
 * // 将列值取反 (0变1, 1变0)
 * Db::table('users')->where('id', 1)->invert('is_active');
 * // 结果: UPDATE users SET is_active = !is_active WHERE id = 1
 * 
 * // 列值递增
 * Db::table('users')->where('id', 1)->inc('login_count');
 * // 结果: UPDATE users SET login_count = login_count + 1 WHERE id = 1
 * 
 * // 指定递增值的列值递增
 * Db::table('users')->where('id', 1)->inc('score', 5);
 * // 结果: UPDATE users SET score = score + 5 WHERE id = 1
 * 
 * // 列值递减
 * Db::table('users')->where('id', 1)->dec('remaining_attempts');
 * // 结果: UPDATE users SET remaining_attempts = remaining_attempts - 1 WHERE id = 1
 * 
 * // 指定递减值的列值递减
 * Db::table('products')->where('id', 1)->dec('stock', 10);
 * // 结果: UPDATE products SET stock = stock - 10 WHERE id = 1
 * 
 * // 子节点查询示例 (仅支持MySQL 5.7+):
 * // 获取用户及其关联订单
 * $user = Db::table('users AS u')
 *     ->select('u.*')
 *     ->leftJoin('orders AS o', 'o.user_id', '=', 'u.id')
 *     ->joinNode('orders', [
 *         'id' => 'o.id',
 *         'amount' => 'o.amount',
 *         'created_at' => 'o.created_at'
 *     ])
 *     ->where('u.id', 1)
 *     ->group('u.id')  // 必须添加GROUP BY分组
 *     ->get();
 * // 结果: 
 * // [
 * //     'id' => 1,
 * //     'username' => 'test',
 * //     'email' => 'test@example.com',
 * //     'orders' => [
 * //         [
 * //             'id' => 101,
 * //             'amount' => 199.99,
 * //             'created_at' => '2023-01-01 10:00:00'
 * //         ],
 * //         [
 * //             'id' => 102,
 * //             'amount' => 299.99,
 * //             'created_at' => '2023-01-05 14:30:00'
 * //         ]
 * //     ]
 * // ]
 * 
 * // 使用first()方法获取子节点数据
 * $user = Db::table('users AS u')
 *     ->select('u.*')
 *     ->leftJoin('orders AS o', 'o.user_id', '=', 'u.id')
 *     ->joinNode('orders', [
 *         'id' => 'o.id',
 *         'amount' => 'o.amount'
 *     ])
 *     ->where('u.id', 1)
 *     ->group('u.id')
 *     ->first();
 * 
 * // 注意: joinNode 方法依赖 MySQL 5.7+ 的 JSON 函数，在其他数据库中不可用。
 * // 如果需要跨数据库支持，请使用原生SQL或多次查询手动构建嵌套数据。
 */
