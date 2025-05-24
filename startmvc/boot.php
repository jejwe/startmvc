<?php
/**
 * StartMVC超轻量级PHP开发框架
 *
 * @author	Shao Bing QQ858292510
 * @copyright Copyright (c) 2020-2022
 * @license   StartMVC 遵循Apache2开源协议发布，需保留开发者信息。
 * @link	  http://startmvc.com
 */

defined('ENV') or define('ENV', 'development');  // 可以是 development 或 production
if (!defined('DS')) {
    define('DS', DIRECTORY_SEPARATOR);
}

if (defined('STARTMVC_WP_PLUGIN_DIR')) {
    if (!defined('ROOT_PATH')) {
        define('ROOT_PATH', STARTMVC_WP_PLUGIN_DIR);
    }
} else {
    if (!defined('ROOT_PATH')) {
        define('ROOT_PATH', dirname(__DIR__) . DS); // Ensure trailing slash
    }
}

if (version_compare(PHP_VERSION , '7.2', '<')) {
	die('程序要求PHP7+环境版本，当前环境为PHP' . PHP_VERSION . ',请升级服务器环境');
}
// session_start(); // Removed for WordPress integration
//版本号
if (!defined('SM_VERSION')) {
    define('SM_VERSION', '2.3.7');
}
if (!defined('SM_UPDATE')) {
    define('SM_UPDATE', '20250508');
}
// 应用命名空间（请与应用所在目录名保持一致）
if (!defined('APP_NAMESPACE')) {
    define('APP_NAMESPACE', 'app');
}
//应用目录
if (!defined('APP_PATH')) {
    define('APP_PATH', ROOT_PATH . 'app' . DS);
}

//公共入口目录(web站点目录)
if (defined('STARTMVC_WP_PLUGIN_DIR')) {
    if (!defined('BASE_PATH')) {
        define('BASE_PATH', ROOT_PATH);
    }
} else {
    // Original behavior if not in WordPress
    if (!defined('BASE_PATH')) {
        define('BASE_PATH', dirname($_SERVER['SCRIPT_FILENAME']) . DS);
    }
}

//框架目录
if (!defined('CORE_PATH')) {
    define('CORE_PATH', ROOT_PATH . 'startmvc' . DS);
}
//缓存路径
if (!defined('CACHE_PATH')) {
    define('CACHE_PATH', ROOT_PATH . 'runtime' . DS . 'cache' . DS);
}
//临时文件路径
if (!defined('TEMP_PATH')) {
    define('TEMP_PATH', ROOT_PATH . 'runtime' . DS . 'temp' . DS);
}
//配置文件路径
if (!defined('CONFIG_PATH')) {
    define('CONFIG_PATH', ROOT_PATH . 'config' . DS);
}

if (defined('STARTMVC_WP_PLUGIN_URL')) {
    if (!defined('_STATIC_')) {
        define('_STATIC_', STARTMVC_WP_PLUGIN_URL . 'public/static/');
    }
} else {
    // Original behavior if not in WordPress
    if (!defined('_STATIC_')) {
        define('_STATIC_', '/static/');
    }
}

if (!defined('START_MEMORY')) {
    define('START_MEMORY',  memory_get_usage());
}
if (!defined('START_TIME')) {
    define('START_TIME',  microtime(true));
}

// 加载函数库
require __DIR__ . '/function.php';

// 注册自动加载
if (is_file(ROOT_PATH . 'vendor'.DS.'autoload.php')) {
    // 优先使用 Composer 自动加载
    require ROOT_PATH . 'vendor'.DS.'autoload.php';
} else {
    // 框架自动加载
    require __DIR__ . '/autoload.php';
    if (class_exists('Autoload')) { // Ensure Autoload class exists before calling register
        Autoload::register();
    }
}

// 创建应用实例并运行 - This will be handled by WordPress hooks
// $app = new \startmvc\core\App();
// $app->run();