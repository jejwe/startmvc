![StartMVC Logo](https://img.kancloud.cn/a0/3f/a03fbd0f272ec563a545ab568995c1eb_557x223.png "StartMVC Logo")

## StartMVC for WordPress 简介

StartMVC 是一款超轻量级、面向对象的PHP开发框架。此版本经过特别重构和优化，旨在便利WordPress插件的开发。其核心目标是让开发者能够在WordPress环境中使用StartMVC熟悉的项目组织方式（MVC）和开发模式，从而更高效地构建功能丰富的插件。

本项目遵循 Apache2 开源协议。

## 核心优势

StartMVC 框架本身具备以下核心优势：

*   **轻量高效**：框架基础核心代码极简，确保高性能运行。
*   **MVC架构**：采用经典的 Model-View-Controller 分层模式，使代码结构更清晰，易于维护和扩展。
*   **Composer支持**：全面拥抱Composer生态，方便引入第三方库和依赖管理。
*   **约定优于配置**：遵循常见开发约定，减少不必要的配置工作。
*   **灵活扩展**：提供多种扩展机制，如中间件、事件等，方便开发者自定义功能。

**针对WordPress集成的特定优势：**

*   **WordPress内实践MVC**：允许开发者在WordPress插件开发中运用成熟的MVC设计模式。
*   **结构化复杂插件**：借助StartMVC的项目结构，可以更好地组织和管理具有复杂业务逻辑的插件。
*   **复用StartMVC组件**：可以复用已有的StartMVC控制器（Controller）、模型（Model）、视图（View）等组件。
*   **$wpdb集成**：数据库操作已与WordPress的全局 `$wpdb` 对象集成，确保与WordPress数据库操作的兼容性和一致性。

## 目录结构

StartMVC 遵循标准的MVC目录组织方式，主要代码位于 `app` 目录下，通常包含以下子目录：

*   `app/controller`：控制器目录，负责处理用户请求和业务逻辑。
*   `app/model`：模型目录，负责数据处理和数据库交互。
*   `app/view`：视图目录，负责展示数据和用户界面。

当作为WordPress插件使用时，此核心的 `app` 目录结构将得以保留，使得插件内部的代码组织清晰、规范。其他框架目录如 `config`（配置文件）、`public`（Web可访问资源，在WordPress中通常指向插件的公共资源目录）、`startmvc`（框架核心）等也维持其原有结构和功能。

## 安装与激活 (作为 WordPress 插件)

1.  **下载与放置**：
    *   获取 StartMVC for WordPress 插件包。
    *   将整个插件文件夹（例如 `startmvc-wp-main` 或您重命名后的文件夹）上传到您的 WordPress 安装目录下的 `wp-content/plugins/` 目录中。

2.  **激活插件**：
    *   登录到您的 WordPress 后台管理界面。
    *   导航到“插件” > “已安装插件”页面。
    *   在插件列表中找到 "StartMVC WordPress Integration"（或您在插件头中定义的名称）。
    *   点击“激活”链接。

## 基本使用理念 (在 WordPress 中)

StartMVC for WordPress 插件的核心入口文件是 `startmvc-wp.php`。此文件在插件被激活时加载 StartMVC 框架的核心引导程序 `startmvc/boot.php`，从而使得框架的功能在 WordPress 环境中可用。

要在您的插件中实际使用 StartMVC 的功能（如控制器和方法），您通常会通过以下方式：

*   **WordPress 动作钩子 (Action Hooks)**：将特定的 StartMVC 控制器方法附加到 WordPress 的动作钩子上。
*   **WordPress 短代码 (Shortcodes)**：创建一个短代码，当该短代码在文章或页面中被使用时，执行相应的 StartMVC 控制器方法。

**简单示例：**

1.  **创建一个简单的 StartMVC 控制器方法**：

    在您的插件的 `app/controller/DemoController.php` (如果尚不存在，请创建) 文件中：

    ```php
    <?php
    namespace app\controller;

    use startmvc\core\Controller;

    class DemoController extends Controller
    {
        public function helloWorld()
        {
            // 直接输出，或者更推荐地，返回给视图
            echo "Hello World from StartMVC in WordPress!"; 
            // 或者: return $this->view->render('demo/hello', ['message' => 'Hello World!']);
        }
    }
    ?>
    ```

2.  **通过 WordPress 动作钩子调用**：

    在您的插件主文件 `startmvc-wp.php` 或一个专门的钩子管理文件中添加：

    ```php
    <?php
    // In startmvc-wp.php or a hooks file

    add_action('wp_loaded', 'my_startmvc_hello_world_action'); 

    function my_startmvc_hello_world_action() {
        // 确保 StartMVC 应用已初始化 (通常 boot.php 会处理基础初始化)
        // 在实际应用中，可能需要一个更完善的引导或服务容器来获取控制器实例
        if (class_exists('app\\controller\\DemoController')) {
            $demoController = new \app\controller\DemoController();
            $demoController->helloWorld();
        }
    }
    ?>
    ```

    或者，**通过短代码调用**：

    ```php
    <?php
    // In startmvc-wp.php or a shortcodes file

    add_shortcode('startmvc_hello', 'my_startmvc_hello_shortcode');

    function my_startmvc_hello_shortcode($atts) {
        // 捕获输出而不是直接 echo，因为短代码需要返回内容
        ob_start();
        if (class_exists('app\\controller\\DemoController')) {
            $demoController = new \app\controller\DemoController();
            $demoController->helloWorld(); 
        }
        return ob_get_clean();
    }
    ?>
    ```
    然后在您的 WordPress 文章或页面中使用 `[startmvc_hello]`。

## 数据库

当 StartMVC 集成到 WordPress 中时，框架的数据库操作将通过 WordPress 的全局数据库对象 `$wpdb` 进行。这意味着：

*   **无需额外配置**：您不需要在 StartMVC 的 `config/database.php` 文件中配置数据库连接信息，框架会自动使用 WordPress 已建立的数据库连接。
*   **一致性**：所有数据库交互都通过 `$wpdb`，确保了与 WordPress 核心及其他插件的数据操作的兼容性和一致性。
*   **模型层集成**：StartMVC 的模型（Model）层将内部使用 `$wpdb` 来执行查询、插入、更新和删除等操作。您可以在模型中使用 `$this->db()` (或其他类似方法，取决于 `DbCore` 的具体实现) 来获取 `$wpdb` 的一个适配实例。

## 路由 (在 WordPress 环境下)

在 WordPress 环境中，StartMVC 的传统路由机制需要适配 WordPress 的URL结构和请求处理流程。通常可以通过以下方式实现：

*   **WordPress 动作参数**：通过特定的URL参数来指定要调用的 StartMVC 控制器和方法。例如，一个请求可能是 `yoursite.com/wp-admin/admin-ajax.php?action=my_plugin_action&sm_route=/demo/helloWorld` 或者在自定义的页面模板中使用 `yoursite.com/my-custom-page/?sm_route=/controller/action`。
*   **WordPress Rewrite Rules API**：对于更友好的URL，可以结合 WordPress 的 Rewrite Rules API 将特定的URL模式映射到 StartMVC 的请求处理逻辑上。这通常需要在插件激活时刷新重写规则。
*   **短代码或管理页面特定路由**：对于由短代码触发的逻辑，或在插件的自定义管理页面中，路由通常更为直接，由处理该短代码或管理页面的函数内部逻辑来实例化和调用相应的 StartMVC 控制器。

目标是提供一种清晰、可管理的方式，通过URL或WordPress内部机制（如AJAX动作、短代码）来精确调用 StartMVC 应用内的控制器方法。

## 静态资源 (CSS, JS)

在 StartMVC for WordPress 插件中，管理和引用 CSS、JavaScript 等静态资源非常重要。正确的方法是使用 WordPress 提供的函数，以确保URL的正确性和兼容性。

框架在 `startmvc/boot.php` 中定义了 `_STATIC_`常量（如果通过 `STARTMVC_WP_PLUGIN_URL` 正确设置），它通常指向插件内部的 `public/static/` 目录的URL。

**推荐引用方式：**

假设您的插件主文件是 `startmvc-wp.php`，并且您在 `public/static/css/style.css` 存放了一个样式文件。

*   **使用 `STARTMVC_WP_PLUGIN_URL` 和 `_STATIC_`（如果 `_STATIC_` 已配置为URL路径）**：

    如果您在 `boot.php` 中将 `_STATIC_` 定义为相对于插件URL的路径 (例如 `public/static/`)，则可以直接拼接：

    ```php
    // 在需要排队脚本或样式的地方
    $style_url = STARTMVC_WP_PLUGIN_URL . 'public/static/css/style.css';
    wp_enqueue_style('my-plugin-style', $style_url, [], '1.0.0');

    $script_url = STARTMVC_WP_PLUGIN_URL . 'public/static/js/script.js';
    wp_enqueue_script('my-plugin-script', $script_url, ['jquery'], '1.0.0', true);
    ```
    这是更直接和推荐的方式，因为它依赖于 `STARTMVC_WP_PLUGIN_URL` 这个在 `startmvc-wp.php` 中定义的标准插件URL常量。

*   **或者使用 WordPress 的 `plugins_url()` 函数**：

    如果您更倾向于使用 `plugins_url()`，可以这样做：

    ```php
    // __FILE__ 在插件主文件中通常指向 startmvc-wp.php
    // 如果在其他文件中，需要传递正确的基准文件路径
    $style_url = plugins_url('public/static/css/style.css', STARTMVC_WP_PLUGIN_DIR . 'startmvc-wp.php');
    wp_enqueue_style('my-plugin-style', $style_url, [], '1.0.0');

    $script_url = plugins_url('public/static/js/script.js', STARTMVC_WP_PLUGIN_DIR . 'startmvc-wp.php');
    wp_enqueue_script('my-plugin-script', $script_url, ['jquery'], '1.0.0', true);
    ```

确保在合适的地方（例如，通过 `admin_enqueue_scripts` 或 `wp_enqueue_scripts` 动作钩子）排队您的脚本和样式。

## Composer 支持与扩展 (Composer Support and Extensions)

StartMVC 框架本身支持 Composer 来管理项目的依赖。当 StartMVC 作为 WordPress 插件的一部分使用时，您仍然可以在插件的特定目录结构内利用 Composer 来引入和管理额外的PHP库。

例如，如果您开发的插件需要一些特定的第三方PHP组件（如特殊的API客户端、数据处理库等），您可以在插件的根目录或一个指定的子目录（如 `vendor/`）中维护一个 `composer.json` 文件，并通过 Composer 来安装这些依赖。

**请注意**：

*   在WordPress插件中使用Composer时，需要确保自动加载机制（`vendor/autoload.php`）被正确引入。`startmvc/boot.php` 文件已包含尝试加载 `vendor/autoload.php` 的逻辑（如果它存在于 `ROOT_PATH` 下的 `vendor` 目录，其中 `ROOT_PATH` 通常是插件的根目录）。
*   管理依赖时，需注意避免与 WordPress 核心或其他插件可能存在的库版本冲突。

## 社区与贡献 (Community and Contribution)

*   **官方网站**: [http://www.startmvc.com](http://www.startmvc.com)
*   **QQ交流群**: 2 स्टार्टMVC (群号: 2 स्टार्टMVC) - *请注意：原始群号似乎不完整或有误，此处保留了原始格式，实际使用时请替换为正确的群号。*

我们欢迎并鼓励社区成员为 StartMVC 框架，特别是其与 WordPress 的集成方面，做出贡献。如果您有任何改进建议、功能请求或发现任何问题，请通过适当的渠道（如官方网站、QQ群或项目仓库的Issues区，如果未来设立）进行反馈。
