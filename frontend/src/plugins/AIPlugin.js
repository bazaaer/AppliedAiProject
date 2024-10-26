import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';

export default class AIPlugin extends Plugin {
    init() {
        const editor = this.editor;

        // Create the button in the toolbar
        editor.ui.componentFactory.add('myButton', locale => {
            const view = new ButtonView(locale);

            // Button configuration
            view.set({
                label: 'Get Suggestions',
                withText: true,
                tooltip: true
            });

            // Handle the button click
            view.on('execute', () => {
                const editorData = editor.getData();
                
                // Call your API with the editor data
                fetch('https://your-api-url.com/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ text: editorData })
                })
                .then(response => response.json())
                .then(data => {
                    // Handle the API response and show suggestion
                    const suggestion = data.suggestion;
                    console.log('API Response:', suggestion);

                    // Optionally, replace the content in the editor with the suggestion
                    if (window.confirm(`Apply suggestion: "${suggestion}"?`)) {
                        editor.setData(suggestion); // Set the new content in the editor
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });

            return view;
        });
    }
}
