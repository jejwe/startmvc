// StartMVC JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('StartMVC Python Framework loaded!');
    
    // 添加版本信息
    var footer = document.querySelector('footer');
    if (footer) {
        var version = document.createElement('div');
        version.className = 'version';
        version.textContent = 'StartMVC Python v2.3.7';
        footer.appendChild(version);
    }
});