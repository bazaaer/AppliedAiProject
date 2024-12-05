import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';
import icon from '../Icon_3.svg'

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
        previewText = this._sendTextToApi(previewText)
        console.log(previewText)

        editor.setData(previewText);
        const Div = document.createElement('div');
        Div.innerHTML = '<p>Original text score: ???</p><p>New text score: ???</p>';
        Div.style.position = 'absolute';
        Div.style.top = '10vh';
        Div.style.right = '-10vw';
        document.body.appendChild(Div);
    }
    //haal verbeterde tekst van api op
    async _sendTextToApi(text) { // https://klopta.vinnievirtuoso.online/api/docs/index.html https://klopta.vinnievirtuoso.online/api/rewrite
        const requestData = {
            text: text
          };
        const response = await fetch('https://klopta.vinnievirtuoso.online/api/texts/rewrite', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Authorization':'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MzMzODk3MDMsIm5iZiI6MTczMzM4OTcwMywianRpIjoiNmU0OGM5OTUtMDJjYS00YmRhLWI1YmYtMGNhOTA5MzA1N2YwIiwiZXhwIjoxNzMzOTk0NTAzLCJpZGVudGl0eSI6ImFkbWluIiwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIiwidXNlcl9jbGFpbXMiOnsicm9sZSI6ImFkbWluIn19.HzBSQ5EsyOPJoTVxEC8ik0do1X2_O9XSDEJ_7XX9K_I',
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