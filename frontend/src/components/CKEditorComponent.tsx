import React, { useState } from 'react';
import Editor from '@ckeditor/ckeditor5-build-classic';
import { CKEditor } from '@ckeditor/ckeditor5-react';

const CKEditorComponent = () => {
    const [editorData, setEditorData] = useState('');

    const extractSentences = (text) => {
        const plainText = text.replace(/<\/?[^>]+(>|$)/g, "");
        const sentences = plainText.match(/[^.!?]+[.!?]*/g) || [];
        return sentences;
    };

    const logSentences = (data) => {
        const sentences = extractSentences(data);
        console.log("Sentences:", sentences);
    };

    return (
        <div>
            <CKEditor
                editor={Editor}
                data=""
                config={{
                    placeholder: 'Type your content here...',
                }}
                onReady={(editor) => {
                    console.log('Editor is ready to use!', editor);
                }}
                onChange={(event, editor) => {
                    const data = editor.getData();
                    setEditorData(data);
                    logSentences(data);
                    console.log(data);
                }}
                onBlur={(event, editor) => {
                    console.log('Blur.', editor);
                }}
                onFocus={(event, editor) => {
                    console.log('Focus.', editor);
                }}
            />
            <style jsx global>{`
                .ck-editor__editable_inline {
                    min-height: 20rem;
                }
            `}</style>
        </div>
    );
};

export default CKEditorComponent;
