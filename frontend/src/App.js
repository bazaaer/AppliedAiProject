import "./App.css";
// import { useState, useEffect, useReducer, useRef } from "react";
import CKEditorComponent from "./components/CKEditorComponent.js"
import Githubtest from "./components/Github.js"



function App() {
  return (
    <div className="App">
        <h1>My App with CKEditor</h1>
        <CKEditorComponent />
    </div>
    // <div className="App">
    //     <Githubtest />
    // </div>
);
}

export default App;
