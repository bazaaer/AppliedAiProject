import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import Command from '@ckeditor/ckeditor5-core/src/command';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';

export default class HighlightPlugin extends Plugin {
    init() {
        const editor = this.editor;
        
        editor.model.schema.extend('$text', { allowAttributes: 'highlight' });

        editor.conversion.attributeToElement({
            model: 'highlight',
            view: {
                name: 'span',
                classes: 'text-highlight',
            },
            upcastAlso: {
                classes: 'text-highlight',
            },
        });

        editor.commands.add('highlightText', new HighlightCommand(editor));

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

            button.bind('isOn', 'isEnabled').to(command, 'value', 'isEnabled');

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
