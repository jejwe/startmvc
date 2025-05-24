<?php
namespace startmvc\core;

use startmvc\core\db\DbCore;
// Config is not strictly needed here anymore if getInstance handles both paths,
// but keeping it doesn't hurt for now, in case other methods might use it,
// or if non-WP path needs more from it.
use startmvc\core\Config; 

/**
 * 数据库门面类
 * 提供静态方法调用数据库操作
 */
class Db
{
    /**
     * 数据库实例
     * @var DbCore
     */
    protected static $instance;
    
    /**
     * 获取数据库表实例
     * @param string $table 表名
     * @return DbCore
     */
    public static function table($table)
    {
        // This will call the modified getInstance below
        return static::getInstance()->table($table);
    }
    
    /**
     * 获取数据库实例
     * @return DbCore
     * @throws \Exception If database configuration is missing or invalid in non-WordPress context.
     */
    protected static function getInstance()
    {
        if (static::$instance === null) {
            // Check if running in a WordPress environment
            // Using defined('ABSPATH') and function_exists('get_option') for robustness
            if (defined('ABSPATH') && function_exists('get_option')) {
                static::$instance = DbCore::getInstance('wordpress'); // Signal WordPress mode
            } else {
                // Original logic for non-WordPress environment
                // Ensure CONFIG_PATH is defined (it should be by boot.php)
                if (!defined('CONFIG_PATH')) {
                    // This is a fallback, ideally boot.php sets this correctly.
                    // This path assumes Db.php is in startmvc/core/
                    $potential_config_path = realpath(__DIR__ . '/../../config');
                    if ($potential_config_path && is_dir($potential_config_path)) {
                        // Define it if not defined, ensuring trailing slash
                        define('CONFIG_PATH', rtrim($potential_config_path, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR);
                    } else {
                        // If still not defined, critical error
                        throw new \Exception('CONFIG_PATH is not defined. Database configuration cannot be loaded for non-WordPress context.');
                    }
                }

                $db_config_file = CONFIG_PATH . 'database.php';
                
                if (!file_exists($db_config_file)) {
                     throw new \Exception('Database configuration file not found: ' . $db_config_file);
                }
                
                // Use @ to suppress errors from include if file is unreadable, though file_exists should catch most.
                $config = @include $db_config_file;

                // Check if include failed or didn't return an array
                if ($config === false) {
                     throw new \Exception('Failed to include or read database configuration file: ' . $db_config_file);
                }
                if (!is_array($config)) { 
                    throw new \Exception('Database configuration file did not return an array as expected: ' . $db_config_file);
                }

                // Proceed with configuration as before
                if (isset($config['driver']) && !empty($config['driver']) && 
                    isset($config['connections'][$config['driver']]) && is_array($config['connections'][$config['driver']])) {
                    static::$instance = DbCore::getInstance($config['connections'][$config['driver']]);
                } else {
                    throw new \Exception('Database configuration is malformed or "driver" / "connections" section is missing/invalid in ' . $db_config_file);
                }
            }
        }
        return static::$instance;
    }
    
    /**
     * 调用DbCore的其他方法
     * @param string $method 方法名
     * @param array $args 参数
     * @return mixed
     */
    public static function __callStatic($method, $args)
    {
        return call_user_func_array([static::getInstance(), $method], $args);
    }
}
?>
