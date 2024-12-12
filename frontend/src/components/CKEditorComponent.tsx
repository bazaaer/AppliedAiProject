import React, { useState, useContext } from "react";
import Editor from "@ckeditor/ckeditor5-build-classic";
import { CKEditor } from "@ckeditor/ckeditor5-react";
import { AuthContext } from "@/context/authContext"; // Assuming AuthContext is available

const CKEditorComponent: React.FC = () => {
  const { apiKey } = useContext(AuthContext); // Retrieve the API key from context
  const [editorData, setEditorData] = useState("");

  const extractSentences = (text: string) => {
    const plainText = text.replace(/<\/?[^>]+(>|$)/g, "");
    const sentences = plainText.match(/[^.!?]+[.!?]*/g) || [];
    return sentences;
  };

  const logSentences = (data: string) => {
    const sentences = extractSentences(data);
    console.log("Sentences:", sentences);
  };

  return (
    <div>
      <CKEditor
        editor={Editor}
        data=""
        config={{
          placeholder: "Type your content here...",
          apiKey: apiKey || "", // Use the token as the API key
        }}
        onReady={(editor) => {
          console.log("Editor is ready to use!", editor);
        }}
        onChange={(event, editor) => {
          const data = editor.getData();
          setEditorData(data);
          logSentences(data);
          console.log(data);
        }}
        onBlur={(event, editor) => {
          console.log("Blur.", editor);
        }}
        onFocus={(event, editor) => {
          console.log("Focus.", editor);
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
