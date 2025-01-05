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
        const model = editor.model;
        const editorElement = this.editor.ui.view.element;
        const view = editor.editing.view;

        this.selection = model.document.selection;
        this.selectedText = '';
        if (this.selection.isCollapsed) {
            console.log('Niets geselecteerd');
        }
        else {
            const viewRanges = Array.from(this.selection.getRanges()).map(range =>
                editor.editing.mapper.toViewRange(range)
            );
            const domConverter = editor.editing.view.domConverter;
            view.change(writer => {
                for (const viewRange of viewRanges) {

                    const domRange = domConverter.viewRangeToDom(viewRange);

                    const container = document.createElement('div');
                    container.appendChild(domRange.cloneContents());
                    this.selectedText += container.innerHTML;
                }
            });
        }

        let previewText = editor.getData();
        let text = "";
        if (!this.selectedText == '') 
            {
                console.log(`Selected text:${this.selectedText}`);
                text = await this._sendTextToApi(this.selectedText,apiKey)
            }
        else 
        {
            console.log(`Current text:${previewText}`)
            text = await this._sendTextToApi(previewText,apiKey)
        }
        console.log(text)

        if (this.selectedText == '') 
            {
                editor.execute('selectAll');
            }
        if (text == '')
            {
                editor.model.change(writer => {
                writer.setSelection(model.document.getRoot(), 0);});
            }

        const html = `${text}`;
        const viewFragment = editor.data.processor.toView(html);
        const modelFragment = editor.data.toModel(viewFragment);
        editor.model.insertContent(modelFragment);
        editor.editing.view.scrollToTheSelection();

        let originalscore = 0;
        let sentences = "";
        sentences = await this._scoreApi(previewText,apiKey)
        let i = 0
        sentences.forEach(({ score, sentence }) => {
            originalscore += score
            i += 1
        })
        originalscore = Math.round((originalscore/i)*100)/100

        let newText = editor.getData();
        let newscore = 0;
        sentences = await this._scoreApi(newText,apiKey)
        i = 0
        sentences.forEach(({ score, sentence }) => {
            newscore += score
            i += 1
        })
        newscore = Math.round((newscore/i)*100)/100

        const existingDiv = document.getElementById('plugin-div');
        if (existingDiv) {
            existingDiv.remove();
        }
        
        const Div = document.createElement('div');
        Div.id = 'plugin-div';
        Div.innerHTML = `<p style="margin: 0;"><button id="closeBtn" style="
            color: grey;
            border: none;
            border-radius: 5px;
            padding: 0px 5px;
            cursor: pointer;
        ">x</button>Originele score: ${originalscore}</p><p style="margin: 0; text-align: right;">Nieuwe score: ${newscore}</p>`;
        Div.style.position = 'absolute';
        Div.style.top = '5px';
        Div.style.right = '5px';
        Div.style.backgroundColor = 'rgb(240, 240, 240)';
        Div.style.borderRadius = '10px';
        Div.style.border = '1px solid black';
        Div.style.padding = '5px';
        Div.querySelector('#closeBtn').onclick = () => {
            Div.remove();
          };
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
        let newtext = result.data
        console.log(result.msg)
        if (result.data == undefined || result.data == null)
        {
            newtext = ""
        }
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