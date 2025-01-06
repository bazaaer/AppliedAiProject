import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';
import icon from '../Icon_3.svg'

export default class advancedPlugin extends Plugin {
    init() {
        const editor = this.editor;
        const apiKey = editor.config.get('apiKey');

        if (!apiKey) {
            console.warn('No API key provided for testPlugin.');
        }
        
        editor.ui.componentFactory.add('advancedButton', locale => {
            const view = new ButtonView(locale);

            view.set({
                label: 'advanced herschrijven',
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

    async _Replacetext(apiKey) {
        const editor = this.editor;
        const model = editor.model;
        const editorElement = this.editor.ui.view.element;
        const view = editor.editing.view;

        this.selectedText = '';
        let text = "";

        const existingDiv = document.getElementById('plugin-div');
        if (existingDiv) {
            existingDiv.remove();
        }
        const previewDiv = document.getElementById('preview-div');
            if (previewDiv) {
                previewDiv.remove();
            }

        const Div = document.createElement('div');
        Div.id = 'plugin-div';
        Div.innerHTML = `<p style="margin: 0;"><button id="closeBtn" style="
            color: grey;
            border: none;
            border-radius: 5px;
            padding: 0px 5px;
            cursor: pointer;
        ">x</button>
        <textarea id="textInput" style="
            width: calc(100% - 10px);
            height: 60px;
            margin-top: 5px;
            padding: 5px;
            font-size: 14px;
            border: 1px solid grey;
            border-radius: 5px;
        " placeholder="Type your text here..."></textarea></p>
        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
        <button id="rewriteBtn" style="
            background-color: rgb(180, 180, 180);
            color: black;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            cursor: not-allowed;
        " disabled>Herschrijven</button>
        <button id="acceptBtn" style="
            background-color: rgb(180, 180, 180);
            color: black;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            cursor: not-allowed;
        " disabled>Accepteren</button>
        </div>`;
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
        
        const textInput = Div.querySelector('#textInput');
        const rewriteBtn = Div.querySelector('#rewriteBtn');
        const acceptBtn = Div.querySelector('#acceptBtn');

        textInput.addEventListener('input', () => {
            if (textInput.value.trim() !== '') {
                rewriteBtn.disabled = false;
                rewriteBtn.style.cursor = 'pointer';
                rewriteBtn.style.backgroundColor = 'rgb(200, 200, 200)';
            } else {
                rewriteBtn.disabled = true;
                rewriteBtn.style.cursor = 'not-allowed';
                rewriteBtn.style.backgroundColor = 'rgb(180, 180, 180)';
            }
        });
        editorElement.appendChild(Div);

        Div.querySelector('#rewriteBtn').onclick = async () => {
            this.selection = model.document.selection;
            let previewText = editor.getData();

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
            
            if (!this.selectedText == '') 
                {
                    console.log(`Selected text:${this.selectedText}`);
                    console.log(`Input content: ${textInput.value}`)
                    text = await this._sendTextToApi(this.selectedText,textInput.value,apiKey)
                }
            else 
            {
                console.log(`Current text:${previewText}`)
                console.log(`Input content: ${textInput.value}`)
                text = await this._sendTextToApi(previewText,textInput.value,apiKey)
            }
            console.log(text)

            const existingDiv = document.getElementById('preview-div');
            if (existingDiv) {
                existingDiv.remove();
            }

            if (text == "") {
                text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin tempus massa vel suscipit efficitur. Fusce pharetra rhoncus egestas. Donec quis lorem at velit efficitur euismod eu eget justo. Sed mollis ante vitae eros mollis, ut placerat nibh egestas. Cras in ante et massa porta ultrices. Quisque facilisis, augue ultricies egestas pulvinar, libero lorem imperdiet nisl, eu fermentum odio turpis sit amet urna. Quisque sed lorem metus. Morbi vitae sapien ut eros maximus elementum id id ante. Nunc porta ipsum eu pretium mollis. Pellentesque non tempor nunc. Suspendisse sapien est, efficitur gravida neque et, lobortis interdum mi. Nulla at tempor eros. Sed sit amet odio semper, fringilla est id, ultricies est. Quisque vitae tincidunt dui, sit amet aliquam felis. Nunc nec neque nec nisi bibendum molestie. Nunc lacus elit, molestie quis lacus ac, suscipit hendrerit dui. Maecenas pharetra consequat ante, vel facilisis libero ultricies non. Donec et magna dolor. Nullam et justo non orci dapibus hendrerit sed id urna. Suspendisse eleifend urna at purus lobortis, sed iaculis enim porttitor. Duis lobortis ut massa ac suscipit. In et sollicitudin velit. Phasellus porttitor, purus quis fermentum dictum, enim nunc convallis ex, a imperdiet felis velit suscipit felis. Mauris vitae libero tempor sapien dignissim molestie. In eget congue neque. Etiam dignissim, nunc non euismod gravida, est justo aliquet lacus, eget congue metus nibh et turpis. Sed a tellus tempor, tempor enim in, vulputate urna. Donec id enim eget purus porttitor vulputate. Quisque facilisis dui quis lacus commodo elementum. Duis tempor convallis justo, quis consectetur risus. Praesent sed nibh a nibh posuere rhoncus a et nibh. Curabitur finibus lorem vel tortor maximus, in efficitur tellus porta. Aenean blandit viverra ipsum suscipit ullamcorper. Cras lacinia enim ligula, nec dictum mi efficitur bibendum. Aliquam efficitur fermentum urna. Nam lobortis varius tincidunt. Aenean hendrerit vel metus sed tincidunt. Integer leo diam, rhoncus sed ipsum a, commodo bibendum diam. Integer tincidunt urna in est semper, ac lacinia magna ultricies. Integer pretium mattis purus viverra ultrices. Donec egestas ultrices justo dictum sollicitudin. Donec quis dictum odio. Ut suscipit, ipsum ac consequat gravida, justo eros finibus ex, at tristique ipsum leo quis massa. Pellentesque consequat justo nibh, eget hendrerit felis fringilla non. Vestibulum consequat lorem nulla, ut tempus velit elementum quis. Mauris faucibus, ante eget imperdiet ullamcorper, purus mauris consectetur turpis, id congue turpis sapien vitae quam. Donec commodo convallis velit at pharetra. Curabitur tristique nunc et diam consequat elementum. Phasellus sodales elit vel ex tincidunt finibus. Curabitur non dictum lacus. Maecenas suscipit mattis magna, et vulputate mi. Etiam in metus sed ante auctor condimentum. Nullam porta varius rutrum. Sed sagittis tortor quis diam blandit, id eleifend diam bibendum. Cras convallis semper suscipit. Nulla in scelerisque arcu. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer in egestas augue. Morbi felis massa, dapibus eu maximus ut, venenatis quis libero."
            }

            const Div = document.createElement('div');
            Div.id = 'preview-div';
            Div.innerHTML = `<p style="margin: 0;"><button id="closeBtn" style="
                color: grey;
                border: none;
                border-radius: 5px;
                padding: 0px 5px;
                cursor: pointer;
            ">x</button></p><p>${text}</p>`;
            Div.style.position = 'absolute';
            Div.style.top = '155px';
            Div.style.right = '5px';
            Div.style.backgroundColor = 'rgb(240, 240, 240)';
            Div.style.borderRadius = '10px';
            Div.style.border = '1px solid black';
            Div.style.padding = '5px';
            Div.style.maxWidth = '300px';
            Div.style.maxHeight = '200px';
            Div.style.overflowY = 'auto';
            Div.style.resize = 'both';
            Div.style.cursor = 'grab';
            Div.querySelector('#closeBtn').onclick = () => {
                Div.remove();
            };

            let isDragging = false;
            let offsetX, offsetY;

            const isResizeHandle = (e) => {
                const rect = Div.getBoundingClientRect();
                return (
                    e.clientX >= rect.right - 15 &&
                    e.clientY >= rect.bottom - 15 &&
                    e.clientX <= rect.right &&
                    e.clientY <= rect.bottom
                );
            };

            Div.addEventListener('mousedown', (e) => {
                if (e.target.id !== 'closeBtn' && e.target.id !== 'textInput' && e.target.tagName !== 'BUTTON') {
                    if (isResizeHandle(e)) {
                        return;
                    }
                    isDragging = true;
                    offsetX = e.pageX - Div.getBoundingClientRect().left + editorElement.getBoundingClientRect().left;
                    offsetY = e.pageY - Div.getBoundingClientRect().top + editorElement.getBoundingClientRect().top;
                    Div.style.cursor = 'grabbing';
                }
            });

            document.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    Div.style.left = `${e.pageX - offsetX}px`;
                    Div.style.top = `${e.pageY - offsetY}px`;
                }
            });

            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    Div.style.cursor = 'grab';
                }
            });

            editorElement.appendChild(Div);


            acceptBtn.disabled = false;
            acceptBtn.style.cursor = 'pointer';
            acceptBtn.style.backgroundColor = 'rgb(200, 200, 200)';
        };

        Div.querySelector('#acceptBtn').onclick = () => {
            console.log('Accept button clicked!');
            const existingDiv = document.getElementById('preview-div');
            if (existingDiv) {
                existingDiv.remove();
            }

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

            const Div = document.getElementById('plugin-div');
            if (Div) {
                Div.remove();
            }
        };
    }

    async _sendTextToApi(text,user_prompt,apiKey) { // https://klopta.vinnievirtuoso.online/api/docs/index.html https://klopta.vinnievirtuoso.online/api/rewrite
        const requestData = {
            text: text,
            user_prompt: user_prompt
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
}