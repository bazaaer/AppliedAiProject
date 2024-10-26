import { useState, useEffect, useReducer, useRef } from "react";

// function useInput(initialValue) {
//     const [value, setValue] = useState(initialValue);
//     return [
//       {
//         value,
//         onChange: (e) => setValue(e.target.value),
//       },
//       () => setValue(initialValue),
//     ];
//   }

// const query = `
// query {
//   allLifts {
//     name
//     elevationGain
//     status
//   }
// }
// `;

// const opts = {
//   method: "POST",
//   headers: { "Content-type": "applictaion/json"},
//   body: JSON.stringify({ query })
// }

// function Lift({ name, elevationGain, status }) {
//   return (
//     <div>
//       <h1>{name}</h1>
//       <p>{elevationGain} {status}</p>
//     </div>
//   );
// }
const tahoe_peaks = [
  {name: "Freel", elevation: 10891},
  {name: "Monument", elevation: 10067},
  {name: "Pyramid", elevation: 9983},
  {name: "Talac" , elevation: 9735}
];

function List({data,renderItem,renderEmpty}) {
  return !data.length ? renderEmpty : <ul>{data.map((item) => (<li key={item.name}>{renderItem(item)}</li>))}</ul>
}

function Githubtest({ library }) {
  return (
    <List data={tahoe_peaks} renderEmpty={<p>This list is empty</p>} renderItem={item => <>{item.name} - {item.elevation} ft.</>}/>
  )
  // const [emotion, setEmotion] = useState("happy");
  // const [secondary, setSecondary] = useState("tired");
  // const [checked, setChecked] = useReducer((checked) => !checked, false);

  // useEffect(() => {
  //   console.log(`Its ${emotion}`);
  // }, [emotion]);
  // useEffect(() => {
  //   console.log(`Its ${secondary}`);
  // }, [secondary]);

  // const [titleProps, resetTitle] = useInput("");
  // const [colorProps, resetColor] = useInput("#00000");
  // const txtTitle = useRef();
  // const hexColor = useRef();

  // const submit = (e) => {
  //   e.preventDefault();
  //   const title = txtTitle.current.value;
  //   const color = hexColor.current.value;
  //   alert(`${title},${color}`);
  //   txtTitle.current.value = "";
  //   hexColor.current.value = "";
  // };
  // const submit2 = (e) => {
  //   e.preventDefault();
  //   alert(`${titleProps.value},${colorProps.value}`);
  //   resetTitle();
  //   resetColor();
  // };

  // const [data, setData] = useState(null);
  // const [error, setError] = useState(null);
  // const [loading, setLoading] = useState(false);

  // useEffect(() => {
  //   setLoading(true);
  //   fetch(`https://snowtooth.moonhighway.com/`, opts)
  //     .then((response) => response.json())
  //     .then(setData)
  //     .then(() => setLoading(false))
  //     .catch(setError);
  // }, []);
  // if (loading) return <h1>Loading ...</h1>;
  // if (error) 
  //   return <pre>{JSON.stringify(error)}</pre>;
  // if (!data) return null;
  // return (
  //   <div>
  //     {data.data.Alllifts.map((lift) => (
  //       <Lift name={lift.name} 
  //       elevationGain={lift.elevationGain}
  //       status={lift.status}/>
  //   ))}
  //   </div>
  // );

  // return (
  //   <div className="App">
  //     <h1>current emotion is {emotion}</h1>
  //     <button onClick={() => setEmotion("sad")}>Sad</button>
  //     <h2>Current secondary emotion is {secondary}</h2>
  //     <button onClick={() => setSecondary("grateful")}>Grateful</button>
  //     <input type="checkbox" value={checked} onChange={setChecked} />
  //     <label>{checked ? "checked" : "not checked"}</label>
  //     <form onSubmit={submit}>
  //       <input ref={txtTitle} type="text" placeholder="color title ..." />
  //       <input ref={hexColor} type="color" />
  //       <button>Add</button>
  //     </form>
  //     <form onSubmit={submit2}>
  //       <input {...titleProps} type="text" placeholder="color title ..." />
  //       <input {...colorProps} type="color" />
  //       <button>Add</button>
  //     </form>
  //     <h1>Data</h1>
  //   </div>
  // );
}

export default Githubtest;