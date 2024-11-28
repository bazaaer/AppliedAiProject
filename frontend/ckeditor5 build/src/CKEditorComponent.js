import React, { useState } from 'react';
import CustomEditor from '../build/ckeditor';
import { CKEditor } from '@ckeditor/ckeditor5-react';

const CKEditorComponent = () => {
    const [editorData, setEditorData] = useState('');

    const extractSentences = (text) => {
        // Remove HTML tags using a regular expression
        const plainText = text.replace(/<\/?[^>]+(>|$)/g, "");
        
        // Split the plain text into sentences using a regex
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
                editor={CustomEditor}
                data=""
                config={{
                    placeholder: 'Type your content here...'
                }}
                onReady={editor => {
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
            <div>
                <h3></h3>
                <div dangerouslySetInnerHTML={{ __html: editorData }} />
            </div>
        </div>
    );
};

export default CKEditorComponent;