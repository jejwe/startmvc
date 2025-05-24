<?php
/**
 * Plugin Name: StartMVC WordPress Integration
 * Plugin URI: https://example.com/startmvc-wp
 * Description: Integrates the StartMVC framework with WordPress for plugin development.
 * Version: 0.1.0
 * Author: Your Name
 * Author URI: https://example.com
 * License: GPLv2 or later
 * Text Domain: startmvc-wp
 */

// If this file is called directly, abort.
if ( ! defined( 'WPINC' ) ) {
        die;
}

// Define a constant for the plugin's root directory path.
// This will be useful for including other files.
if ( ! defined( 'STARTMVC_WP_PLUGIN_DIR' ) ) {
        define( 'STARTMVC_WP_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );
}

// Define a constant for the plugin's root URL.
// This will be useful for enqueueing assets.
if ( ! defined( 'STARTMVC_WP_PLUGIN_URL' ) ) {
        define( 'STARTMVC_WP_PLUGIN_URL', plugin_dir_url( __FILE__ ) );
}

// Include the StartMVC bootstrapper.
// We'll adjust paths within boot.php in a later step.
require_once STARTMVC_WP_PLUGIN_DIR . 'startmvc/boot.php';

// Placeholder for WordPress activation/deactivation hooks if needed later
// register_activation_hook( __FILE__, 'startmvc_wp_activate' );
// register_deactivation_hook( __FILE__, 'startmvc_wp_deactivate' );

// function startmvc_wp_activate() {
//     // Activation code
// }

// function startmvc_wp_deactivate() {
//     // Deactivation code
// }

// Placeholder for further WordPress integration logic
// add_action('init', 'startmvc_wp_init');
// function startmvc_wp_init() {
//     // Initialize StartMVC app or routing for WordPress
//     // For example: $app = new \startmvc\core\App();
//     // $app->run_for_wordpress_plugin(); // This method would need to be created
// }
?>
