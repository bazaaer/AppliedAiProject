import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';


export default class testPlugin extends Plugin {
    init() {
        const editor = this.editor;
        
        // Create the button in the toolbar
        editor.ui.componentFactory.add('myButton', locale => {
            const view = new ButtonView(locale);

            // Button configuration
            view.set({
                label: 'Get Suggestions',
                icon: '🔘',
                withText: true,
                tooltip: true
            });
            
            // Handle the button click
            view.on('execute', () => {
                    console.log('MyCustomPlugin initialized');
                    const suggestion = "<p>This is a suggestion</p>";
                    console.log('API Response:', suggestion);

                    // Optionally, replace the content in the editor with the suggestion
                    if (window.confirm(`Apply suggestion: "${suggestion}"?`)) {
                        try {
                            editor.setData(suggestion); // Set the new content in the editor
                          } catch (error) {
                            console.error('Error setting data in editor:', error);
                          }
                    }
                });
                return view;
            });

            
        };
    }

