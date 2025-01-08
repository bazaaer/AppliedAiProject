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
        let totalscore = 0;
        let sentences = "";
        if (!this.selectedText == '') 
            {
                console.log(`Selected text:${this.selectedText}`);
                sentences = await this._sendTextToApi(this.selectedText,apiKey)
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

        const previewDiv = document.getElementById('preview-div');
        if (previewDiv) {
            previewDiv.remove();
        }

        const existingDiv = document.getElementById('plugin-div');
        if (existingDiv) {
            existingDiv.remove();
        }
        
        totalscore = Math.round((totalscore/i)*100)/100
        const Div = document.createElement('div');
        Div.id = 'plugin-div';
        Div.innerHTML = `<p style="margin: 0;"><button id="closeBtn" style="
            color: grey;
            border: none;
            border-radius: 5px;
            padding: 0px 5px;
            cursor: pointer;
        ">x</button>Score: ${totalscore} <button id="infoBtn" style="
            background-color: rgb(200, 200, 200);
            color: black;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            cursor: pointer;
        ">?</button></p>`;
        Div.style.position = 'absolute';
        Div.style.top = '5px';
        Div.style.right = '5px';
        Div.style.backgroundColor = 'rgb(240, 240, 240)';
        Div.style.borderRadius = '10px';
        Div.style.border = '1px solid black';
        Div.style.padding = '5px';
        Div.querySelector('#closeBtn').onclick = () => {
            Div.remove();
            const previewDiv = document.getElementById('preview-div');
            if (previewDiv) {
                previewDiv.remove();
            }
          };

        Div.querySelector('#infoBtn').onclick = () => {
            const previewDiv = document.getElementById('preview-div');
                if (previewDiv) {
                    previewDiv.remove();
                }
            sentences.sort((a, b) => a.score - b.score);
            const Div = document.createElement('div');
            Div.id = 'preview-div';
            Div.innerHTML = `<p style="margin: 0;"><button id="closeBtn" style="
                color: grey;
                border: none;
                border-radius: 5px;
                padding: 0px 5px;
                cursor: pointer;
            ">x</button></p>`;
            Div.style.position = 'absolute';
            Div.style.top = '50px';
            Div.style.right = '5px';
            Div.style.backgroundColor = 'rgb(240, 240, 240)';
            Div.style.borderRadius = '10px';
            Div.style.border = '1px solid black';
            Div.style.padding = '5px';
            Div.style.maxWidth = '300px';
            Div.style.maxHeight = '200px';
            Div.style.overflowY = 'auto';
            Div.querySelector('#closeBtn').onclick = () => {
                Div.remove();
            };
            sentences.forEach(item => {
                const rowDiv = document.createElement("div");
                rowDiv.style.display = "flex";
                rowDiv.style.justifyContent = "space-between";
                rowDiv.style.marginBottom = "8px";

                const sentence  = document.createElement("p");
                sentence.textContent = item.sentence;
                sentence.style.margin = "0";

                const number = document.createElement("p");
                number.textContent = `Score: ${Math.round(item.score*100)/100}`;
                number.style.margin = "0";

                rowDiv.appendChild(sentence);
                rowDiv.appendChild(number);
                Div.appendChild(rowDiv);
            });
            editorElement.appendChild(Div);
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