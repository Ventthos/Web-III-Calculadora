import './App.css';
import React, { useState, useEffect, use } from "react";
import { IoIosArrowBack } from "react-icons/io";
import { IoIosArrowForward } from "react-icons/io";


function App() {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [resultado, setResultado] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [modo, setModo] = useState(1);

  const sumar = async () => {
    const res = await fetch(`http://localhost:8089/calculadora/sum?a=${a}&b=${b}`);
    const data = await res.json();
    setResultado(data.resultado);
    obtenerHistorial();
  };

  const manageOperacion = async () => {
    let url = ""
    switch (modo) {
      case 1:
        url = "sum"
        break;
      case 2:
        url = "resta"
        break;
      case 3:
        url = "mult"
        break;
      case 4:
        url = "div"
        break;
      default:
        break;
    }
    const res = await fetch(`http://localhost:8089/calculadora/${url}?a=${a}&b=${b}`);
    const data = await res.json();
    setResultado(data.resultado);
    obtenerHistorial();

  };

  const obtenerHistorial = async () => {
    const res = await fetch("http://localhost:8089/calculadora/historial");
    const data = await res.json();
    setHistorial(data.historial);
  };

  function cambiarModoAdelante() {
    if (modo < 4) {
      setModo(modo + 1);
    } else {
      setModo(1);
    }
  }

  function cambiarModoAtras() {
    if (modo > 1) {
      setModo(modo - 1);
    } else {
      setModo(4);
    }
  }

  function returnModoString(modo) {
    switch (modo) {
      case 1:
        return "Sumar";
      case 2:
        return "Restar";
      case 3:
        return "Multiplicar";
      case 4:
        return "Dividir";
      default:
        return "Modo no válido";
    }
  }

  function returnOperator(modo) {
    switch (modo) {
      case "suma":
        return "+";
      case "resta":
        return "-";
      case "multiplicacion":
        return "*";
      case "division":
        return "/";
      default:
        return "Modo no válido";
    }
  }

  useEffect(() => {
    obtenerHistorial();
  }, []);

  return (
    <div style={{ padding: 20}}>
      <div>
        <h1>Calculadora </h1>
        <div className='botonesRow'>
          <button className='botonArrow' onClick={cambiarModoAtras}><IoIosArrowBack/></button>
          <p>Modo: {returnModoString(modo)}</p>
          <button className='botonArrow' onClick={cambiarModoAdelante}><IoIosArrowForward/></button>
        </div>
        
      </div>

      <div className='display-2-columnas'>
        <div>
          <div className='inputLabel'>
            <label htmlFor='numero1'>Número 1</label>
            <input
              type="number"
              value={a}
              onChange={(e) => setA(e.target.value)}
              placeholder="Número 1"
              name='numero1'
              id='numero1'
            />
          </div>
          <div className='inputLabel'>
            <label htmlFor='numero2'>Número 2</label>
            <input
              type="number"
              value={b}
              onChange={(e) => setB(e.target.value)}
              placeholder="Número 2"
              name='numero2'
              id='numero2'
            />
          </div>
          <button onClick={manageOperacion} className='botonArrow botonEjecutar'>{returnModoString(modo)}</button>
        </div>
        <div className='displayResultado '>
          {resultado !== null && 
            <>
              <p className='blueText'>Resultado: </p>
              <h2>{resultado}</h2>
            </>
          }
        </div>
      </div>
            
      <div style={{marginTop:"2rem"}}>
        <h3>Historial:</h3>
        <ul>
          {historial.map((op, i) => (
            <li key={i}>
              {op.a} {returnOperator(op.operacion)} {op.b} = {op.resultado} ({op.date})
            </li>
          ))}
        </ul>
      </div>
      
    </div>
  );
}

export default App;
