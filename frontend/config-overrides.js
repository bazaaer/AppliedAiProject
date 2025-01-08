const { override } = require('customize-cra');

module.exports = override((config) => {
    // Find the existing rule for SVG files
    const rule = config.module.rules.find(rule => rule.test && rule.test.test('.svg'));
    
    // Modify the existing rule to handle namespaces
    if (rule) {
        rule.use = [
            {
                loader: '@svgr/webpack',
                options: {
                    throwIfNamespace: false, // This allows namespace tags
                },
            },
            ...rule.use, // Keep any other loaders
        ];
    }

    return config;
});
