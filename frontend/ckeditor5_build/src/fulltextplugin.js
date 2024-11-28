import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';
import { createDropdown } from '@ckeditor/ckeditor5-ui/src/dropdown/utils';
import View from '@ckeditor/ckeditor5-ui/src/view';
import icon from './Icon_3.svg'

export default class fulltextPlugin extends Plugin {
    init() {
        const editor = this.editor;
        
        editor.ui.componentFactory.add('fulltextButton', locale => {
            const dropdown = createDropdown(locale);

            dropdown.buttonView.set({
                label: 'tekst herschrijven',
                icon: icon,
                withText: false,
                tooltip: true
            });
            console.log('MyCustomPlugin initialized 2');
            dropdown.panelView.extendTemplate({
                attributes: {
                    style: {
                        'border-radius': '8px',
                        'border': '1px solid #ccc',
                    }
                }
            });

            this._addPreviewContent(dropdown);

            return dropdown;
            });
        console.log('MyCustomPlugin initialized 1');
    }
    //maakt dropdown aan 
    _addPreviewContent(dropdown) {
        const editor = this.editor;

        let previewText = "Click button to generate text"

        const previewTextView = new View();
        previewTextView.setTemplate({
            tag: 'div',
            children: [
                {
                    text: previewText
                }
            ],
            attributes: {
                style: {
                    'min-width': '200px',
                    'max-width': '300px',
                    'white-space': 'pre-wrap',
                    'overflow-wrap': 'break-word',
                    'padding': '10px',
                    'border': '1px solid #ccc',
                    'border-radius': '4px',
                    'background-color': '#f9f9f9'
                }
            }
        });

        const loadCurrentTextButton = new ButtonView();
        loadCurrentTextButton.set({
            label: 'Load Current Text',
            withText: true,
            tooltip: true
        });

        loadCurrentTextButton.on('execute', () => {
            previewText = editor.getData();
            this._sendTextToApi(previewText).then(apiResponse => {
                previewText = apiResponse;
            });
            //verwijdert alle html tags zonder de structuur te veranderen
            const plainText = previewText.replace(/<\/(h[1-6]|p)>/g, '\n').replace(/<(h[1-6]|p)[^>]*>/g, '\n').replace(/<br\s*\/?>/g, '\n').replace(/<\/?[^>]+(>|$)/g, "").replace(/\n\s*\n/g, '\n').trim();
            previewTextView.element.textContent = plainText;
            console.log(previewText)
        });

        const acceptButton = new ButtonView();
        acceptButton.set({
            label: 'Accept Change',
            withText: true,
            tooltip: true
        });

        acceptButton.on('execute', () => {
            editor.setData(previewText);
            dropdown.isOpen = false;
        });
        // nieuwe container anders staan de knoppen verkeerd
        const buttonContainer = new View();
        buttonContainer.setTemplate({
            tag: 'div',
            attributes: {
                style: {
                    display: 'flex',
                    'flex-direction': 'row',
                    'justify-content': 'space-between',
                    'align-items': 'center',
                    width: '100%'
                }
            },
            children: [
                loadCurrentTextButton,
                acceptButton
            ]
        });

        dropdown.panelView.children.add(previewTextView);
        dropdown.panelView.children.add(buttonContainer);
    }
    //haal verbeterde tekst van api op
    async _sendTextToApi(text) {
        const response = await fetch('https://klopta.vinnievirtuoso.online/api/rewrite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });

        // if (!response.ok) {
        //     throw new Error('API request failed');
        // }

        const result = await response.json();
        //tijdelijke aanpassing
        const newtext = result
        return newtext;
    }
}