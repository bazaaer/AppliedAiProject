import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';
import icon from '../Icon_3.svg'

export default class testPlugin extends Plugin {
    init() {
        const editor = this.editor;
        const apiKey = editor.config.get('apiKey');

        if (!apiKey) {
            console.warn('No API key provided for testPlugin.');
        }
        
        editor.ui.componentFactory.add('testButton', locale => {
            const view = new ButtonView(locale);

            view.set({
                label: 'tekst herschrijven',
                icon: icon,
                withText: false,
                tooltip: true
            });
            view.on('execute', () => {
                this._Replacetext(apiKey);
            });

            return view;
            });
    }
    //vervangt tekst en laat scores zien
    _Replacetext(apiKey) {
        const editor = this.editor;
        const editorElement = this.editor.ui.view.element;

        let previewText = editor.getData();
        previewText = this._sendTextToApi(previewText,apiKey)
        console.log(previewText)

        editor.setData(previewText);
        const Div = document.createElement('div');
        Div.innerHTML = '<p>Original text score: ???</p><p>New text score: ???</p>';
        Div.style.position = 'absolute';
        Div.style.top = '0px';
        Div.style.right = '10px';
        editorElement.appendChild(Div);
    }
    //haal verbeterde tekst van api op
    async _sendTextToApi(text,apiKey) { // https://klopta.vinnievirtuoso.online/api/docs/index.html https://klopta.vinnievirtuoso.online/api/rewrite
        const requestData = {
            text: text
          };
        const response = await fetch('https://klopta.vinnievirtuoso.online/api/model/rewrite', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Authorization':`Bearer ${apiKey}` ,
                'Content-Type': 'application/json'

            },
            body: JSON.stringify(requestData)
        }).catch(error => {
            console.error('Error:', error);
          });

        const result = await response.json();
        //tijdelijke aanpassing
        const newtext = result.data.text
        console.log(result.msg)
        console.log(`new text: ${newtext}`)
        return newtext;
    }
}