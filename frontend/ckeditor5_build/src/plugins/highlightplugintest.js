import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import Command from '@ckeditor/ckeditor5-core/src/command';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';


export default class HighlightPlugin extends Plugin {
    static get pluginName() {
        return 'HighlightPlugin';
    }

    init() {
        const editor = this.editor;
        
        editor.model.schema.extend('$text', { allowAttributes: 'highlight' });

        editor.conversion.attributeToElement({
            model: 'highlight',
            view: {
                name: 'span',
                classes: 'text-highlight', // Define a CSS class for highlighting
            },
            upcastAlso: {
                classes: 'text-highlight',
            },
        });

        // Register the command
        editor.commands.add('highlightText', new HighlightCommand(editor));

        // Add the button to the UI
        editor.ui.componentFactory.add('highlightText', (locale) => {
            const command = editor.commands.get('highlightText');
            const button = new ButtonView(locale);

            button.set({
                label: 'Highlight',
                icon: '',
                tooltip: true,
                withText: true,
                isToggleable: true,
            });

            // Bind button state to command state
            button.bind('isOn', 'isEnabled').to(command, 'value', 'isEnabled');

            // Execute command on button click
            this.listenTo(button, 'execute', () => {
                editor.execute('highlightText');
            });

            return button;
        });
    }
}

class HighlightCommand extends Command {
    execute() {
        const editor = this.editor;
        const model = editor.model;

        model.change((writer) => {
            const selection = model.document.selection;
            const isHighlighted = selection.hasAttribute('highlight');

            if (isHighlighted) {
                writer.removeSelectionAttribute('highlight');
            } else {
                writer.setSelectionAttribute('highlight', true);
            }
        });
    }

    refresh() {
        const model = this.editor.model;
        const selection = model.document.selection;
        this.value = selection.hasAttribute('highlight');
        this.isEnabled = model.schema.checkAttributeInSelection(selection, 'highlight');
    }
}
