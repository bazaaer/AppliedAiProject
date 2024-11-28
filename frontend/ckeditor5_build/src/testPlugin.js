import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';
import icon from './Icon_3.svg'

export default class testPlugin extends Plugin {
    init() {
        const editor = this.editor;
        
        editor.ui.componentFactory.add('testButton', locale => {
            const view = new ButtonView(locale);

            view.set({
                label: 'tekst herschrijven',
                icon: icon,
                withText: false,
                tooltip: true
            });
            console.log('MyCustomPlugin initialized 2');
            view.on('execute', () => {
                this._Replacetext();
            });

            return view;
            });
        console.log('MyCustomPlugin initialized 1');
    }
    //vervangt tekst en laat scores zien
    _Replacetext() {
        const editor = this.editor;

        let previewText = editor.getData();
        this._sendTextToApi(previewText).then(apiResponse => {
            previewText = apiResponse;
        });
        console.log(previewText)

        editor.setData(previewText);
        const Div = document.createElement('div');
        Div.innerHTML = '<p>Original text score: ???</p><p>New text score: ???</p>';
        Div.style.position = 'fixed';
        Div.style.top = '10vh';
        Div.style.right = '10vw';
        document.body.appendChild(Div);
    }
    //haal verbeterde tekst van api op
    async _sendTextToApi(text) { // https://klopta.vinnievirtuoso.online/api/docs/index.html https://klopta.vinnievirtuoso.online/api/rewrite
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