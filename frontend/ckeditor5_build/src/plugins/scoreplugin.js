import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';
import icon from '../check-mark.svg'

export default class scorePlugin extends Plugin {
    init() {
        const editor = this.editor;
        const apiKey = editor.config.get('apiKey');
        
        if (!apiKey) {
            console.warn('No API key provided for scorePlugin.');
        }

        editor.ui.componentFactory.add('scoreButton', locale => {
            const view = new ButtonView(locale);

            view.set({
                label: 'score',
                icon: icon,
                withText: false,
                tooltip: true
            });
            view.on('execute', () => {
                this._Scoretext(apiKey);
            });

            return view;
            });
    }
    async _Scoretext(apiKey) {
        const editor = this.editor;
        const model = editor.model;
        const editorElement = this.editor.ui.view.element;
        const view = editor.editing.view;
        this.selection = model.document.selection;
        this.selectedText = '';
        if (this.selection.isCollapsed) {
            console.log('Nothing is selected!');
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
            console.log(`Selected text:${this.selectedText}`);
        }

        let previewText = editor.getData();
        let totalscore = 0;
        let sentences = "";
        if (!this.selectedText == '') 
            {
                sentences = await this._sendTextToApi(selectedText,apiKey)
            }
        else 
        {
            console.log(`Current text:${previewText}`)
            sentences = await this._sendTextToApi(previewText,apiKey)
        }
        
        console.log(sentences)
        let i = 0
        sentences.forEach(({ score, sentence }) => {
            totalscore += score
            i += 1
        })
        
        totalscore = Math.round((totalscore/i)*100)/100
        const Div = document.createElement('div');
        Div.innerHTML = `<p style="margin: 0;"><button id="closeBtn" style="
            color: grey;
            border: none;
            border-radius: 5px;
            padding: 0px 5px;
            cursor: pointer;
        ">x</button>Score: ${totalscore}</p>`;
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

        previewText = editor.getData();
        console.log(previewText)
    }

    async _sendTextToApi(text,apiKey) {
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