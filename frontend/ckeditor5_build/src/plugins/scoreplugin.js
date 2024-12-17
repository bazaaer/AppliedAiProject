import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';
import icon from '../Icon_3.svg'

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
        // const style = document.createElement('style');
        // style.type = 'text/css';
        // style.innerHTML = `
        //     .highlight-high { background-color: #a8e6cf; }
        //     .highlight-medium { background-color: #ffd3b6; }
        //     .highlight-low { background-color: #ffaaa5; }
        // `;
        // document.head.appendChild(style);

        let previewText = editor.getData();
        let totalscore = 0;
        let sentences = "";
        sentences = await this._sendTextToApi(previewText,apiKey)
        // sentences = [
        // {
        //     "score": 0.7916542291641235,
        //     "sentence": "De vondst van het kanon past zeer goed in het plaatje van stad Antwerpen als militair steunpunt onder het Napoleontisch bewind. Tijdens de Franse periode (1794-1815) had Napoleon Bonaparte een grote interesse in de Scheldestad omwille van het strategisch belang. Hij maakte van Antwerpen een moderne haven met marine arsenaal en versterkte de stad op tal van plaatsen."
        // },
        // {
        //     "score": 0.9503110647201538,
        //     "sentence": "Ik heb absctracte honger maar dit is een rigoreus voorbeeld van een slechte zin die egenlijk veel te langdradig is voor wat ik wil zeggen dus zou dit niet goed mogen zijn en zou de scorer dus een slecht resultaat moeten geven okay :)"
        // }
        // ]
        let i = 0
        sentences.forEach(({ score, sentence }) => {
            totalscore += score
            i += 1
        })
        totalscore = Math.round((totalscore/i)*100)/100
        const Div = document.createElement('div');
        Div.innerHTML = `<p style="margin: 0;">Score: ${totalscore}</p>`;
        Div.style.position = 'absolute';
        Div.style.top = '5px';
        Div.style.right = '5px';
        Div.style.backgroundColor = 'rgb(240, 240, 240)';
        Div.style.borderRadius = '10px';
        Div.style.border = '1px solid black';
        Div.style.padding = '5px';
        editorElement.appendChild(Div);

        // model.change(writer => {
        //     for (const range of model.markers.getMarkersGroup('highlight')) {
        //         writer.removeMarker(range);
        //     }

        //     const root = model.document.getRoot();
        //     const textToHighlight = sentences[0].sentence;

        //     for (const range of this.findTextRanges(root, textToHighlight)) {
        //         writer.addMarker(`highlight_${range.start.path.join('_')}`, {
        //             range,
        //             usingOperation: false,
        //             affectsData: false,
        //         });

        //         writer.setAttribute('highlight', true, range);
        //     }
        // });
        previewText = editor.getData();
        console.log(previewText)
    }
    // findTextRanges(root, textToHighlight) {
    //     const editor = this.editor;
    //     const model = editor.model;
    //     const ranges = [];
    //     console.log(root)
    //     console.log(textToHighlight)
    //     for (const child of root.getChildren()) {
    //         if (child.is('element')) {
    //             const text = this.getElementText(child); 

    //             let index = text.indexOf(textToHighlight);
    //             while (index !== -1) {
    //                 const startOffset = index;
    //                 const endOffset = startOffset + textToHighlight.length;

    //                 const startPosition = model.createPositionAt(child, startOffset);
    //                 const endPosition = model.createPositionAt(child, endOffset);

    //                 const range = model.createRange(startPosition, endPosition);
    //                 ranges.push(range);

    //                 index = text.indexOf(textToHighlight, endOffset);
    //             }
    //         }
    //     }

    //     return ranges;
    // }
    // getElementText(element) {
    //     let text = '';
    
    //     for (const child of element.getChildren()) {
    //         if (child.is('text')) {
    //             text += child.data;
    //         } else if (child.is('element')) {
    //             text += this.getElementText(child);
    //         }
    //     }
    
    //     return text;
    // }
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