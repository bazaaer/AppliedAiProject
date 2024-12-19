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
    async _Replacetext(apiKey) {
        const editor = this.editor;
        const editorElement = this.editor.ui.view.element;

        let previewText = editor.getData();
        console.log(`Current text:${previewText}`)
        let text = ""
        text = await this._sendTextToApi(previewText,apiKey)
        console.log(text)

        let sentences = "";
        let originalscore = 0;
        sentences = await this._scoreApi(previewText,apiKey)
        let i = 0
        sentences.forEach(({ score, sentence }) => {
            originalscore += score
            i += 1
        })
        originalscore = Math.round((originalscore/i)*100)/100

        let newscore = 0;
        sentences = await this._scoreApi(text,apiKey)
        i = 0
        sentences.forEach(({ score, sentence }) => {
            newscore += score
            i += 1
        })
        newscore = Math.round((newscore/i)*100)/100

        editor.setData(`${text}`);
        const Div = document.createElement('div');
        Div.innerHTML = `<p style="margin: 0;"><button id="closeBtn" style="
            color: grey;
            border: none;
            border-radius: 5px;
            padding: 0px 5px;
            cursor: pointer;
        ">x</button>Originele score: ${originalscore}</p><p style="margin: 0; align="right"">Nieuwe score: ${newscore}</p>`;
        Div.style.position = 'absolute';
        Div.style.top = '5px';
        Div.style.right = '5px';
        Div.style.backgroundColor = 'rgb(240, 240, 240)';
        Div.style.borderRadius = '10px';
        Div.style.border = '1px solid black';
        Div.style.padding = '5px';
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
        console.log(result)
        //tijdelijke aanpassing
        const newtext = result.data
        console.log(result.msg)
        console.log(`new text: ${newtext}`)
        return `${newtext}`;
    }
    async _scoreApi(text,apiKey) {
        const requestData = {
            text: text
          };
        const response = await fetch('https://klopta.vinnievirtuoso.online/api/model/score', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Authorization':`Bearer ${apiKey}`,
                'Content-Type': 'application/json'

            },
            body: JSON.stringify(requestData)
        }).catch(error => {
            console.error('Error:', error);
          });
        const result = await response.json();
        console.log(result)
        //tijdelijke aanpassing
        const sentences = result.sentence_scores
        return sentences;
    }
}