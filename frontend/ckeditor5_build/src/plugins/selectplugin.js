import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import ButtonView from '@ckeditor/ckeditor5-ui/src/button/buttonview';

export default class SelectionModePlugin extends Plugin {
    init() {
        const editor = this.editor;

        editor.ui.componentFactory.add('selectionMode', locale => {
            const view = new ButtonView(locale);
            view.set({
                label: 'Selection Mode',
                withText: true,
                tooltip: true
            });

            view.on('execute', () => {
                this._enableSelectionMode();
            });

            return view;
        });
    }

    _enableSelectionMode() {
        const editor = this.editor;

        this.isSelectionModeActive = true;

        this.selectedText = '';

        editor.editing.view.document.on('mousedown', this._onMouseDown.bind(this));
        editor.editing.view.document.on('mouseup', this._onMouseUp.bind(this));
    }

    _onMouseDown(event) {
        if (this.isSelectionModeActive) {
            this.selectedText = '';
            // nodig voor later
            const view = this.editor.editing.view;
            this.startPos = view.document.selection.getFirstRange();
        }
    }

    _onMouseUp(event) {
        if (this.isSelectionModeActive) {
            const editor = this.editor;
            const model = editor.model;
            const view = editor.editing.view;
            this.selection = model.document.selection;

            const viewRanges = Array.from(this.selection.getRanges()).map(range =>
                editor.editing.mapper.toViewRange(range)
            );

            const domConverter = editor.editing.view.domConverter;
            this.selectedText = '';
            // dit gedeelte werkt niet, is waarschijnlijk ook niet nodig
            view.change(writer => {
                for (const viewRange of viewRanges) {

                    const domRange = domConverter.viewRangeToDom(viewRange);

                    const container = document.createElement('div');
                    container.appendChild(domRange.cloneContents());
                    this.selectedText += container.innerHTML;
                }
            });

            console.log(`Selected text:${this.selectedText}`);
            this._showConfirmButton();
        }
    }

    _showConfirmButton() {
        const confirmButton = document.createElement('button');
        confirmButton.innerText = 'Confirm Selection';
        confirmButton.style.position = 'fixed';
        confirmButton.style.bottom = '10vh';
        confirmButton.style.right = '10vw';
        document.body.appendChild(confirmButton);

        confirmButton.addEventListener('click', () => {
            this._confirmSelection();
            document.body.removeChild(confirmButton);
        });
    }

    _confirmSelection() {
        const editor = this.editor;
        const model = editor.model;
        const dataProcessor = this.editor.data.processor;
        const viewFragment = dataProcessor.toView(this.selectedText);
        const modelFragment = this.editor.data.toModel(viewFragment);

        if (this.selectedText) {
            model.change(writer => {
                for (const range of this.selection.getRanges()) {
                    writer.remove(range);
                    writer.insert(modelFragment, range.start);
                }
            });
        }

        this.isSelectionModeActive = false;
        this.selectedText = '';
    }
}
