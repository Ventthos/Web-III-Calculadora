import './App.css';
import React, { useState, useEffect, useReducer } from "react";
import { IoIosArrowBack } from "react-icons/io";
import { IoIosArrowForward } from "react-icons/io";
import { InputLabel } from './components/InputLabel';

const initialState = {
  tipoOperacion: "todos",
  fecha: "",
  ordenarPor: "ninguno",
  orden: "asc",
};

function reducer(state, action) {
  switch (action.type) {
    case "SET_OPERACION":
      return { ...state, tipoOperacion: action.payload };
    case "SET_FECHA":
      return { ...state, fecha: action.payload };
    case "SET_ORDENAR":
      return { ...state, ordenarPor: action.payload };
    case "SET_ORDEN":
      return { ...state, orden: action.payload };
    default:
      return state;
  }
}

function App() {
  const [resultado, setResultado] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [modo, setModo] = useState(1);
  const [cantidadNumeros, setCantidadNumeros] = useState(2)
  const [numeros, setNumeros] = useState([0, 0]);
  const [state, dispatch] = useReducer(reducer, initialState);

  
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
        return "Modo no válido";
        break;
    }


    const res = await fetch(`http://localhost:8089/calculadora/${url}`,{
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify({ numeros })
    });
    const data = await res.json();

    if(data.detail?.error){
      alert(data.detail.error)
      return;
    }
    setResultado(data.resultado);
    obtenerHistorial();

  };

  function formatUrl(){
    const url = new URL("http://localhost:8089/calculadora/historial")
    if(state.tipoOperacion !== "todos"){
      url.searchParams.append("operacion", state.tipoOperacion)
    }
    if(state.fecha !== ""){
      url.searchParams.append("fecha", state.fecha)
    }
    if(state.ordenarPor !== "ninguno"){
      url.searchParams.append("ordenarPor", state.ordenarPor)
    }
    url.searchParams.append("orden", state.orden)
    return url.toString()
  }
  
  const obtenerHistorial = async () => {
    const res = await fetch(formatUrl());
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

  function restarCantidadDeNumeros(){
    if(cantidadNumeros > 2){
      setCantidadNumeros((prev)=>prev-1)
    }
  }
  
  function sumarCantidadDeNumeros(){
    setCantidadNumeros((prev)=>prev+1)
  }

  function handleNumeroChange(index, value) {
    setNumeros(prev => {
      const newArr = [...prev];
      newArr[index] = value;
      return newArr;
    })
  }

  function formatOperation(op) {
    const operador = returnOperator(op.operacion)
    return op.numeros.join(` ${operador} `) + ` = ${op.resultado}`
  }

  useEffect(() => {
    obtenerHistorial();
  }, []);

  useEffect(() => {
    obtenerHistorial()
    
  }, [state]);

  useEffect(() => {
    setNumeros(prev => {
      const newArr = [...prev];
      while (newArr.length < cantidadNumeros) newArr.push(0);
      while (newArr.length > cantidadNumeros) newArr.pop();
      return newArr;
    });
  }, [cantidadNumeros]);

  return (
    <div style={{ padding: 20}}>
      <div>
        <h1>Calculadora</h1>
        <div className='botonesContainer'>
          <div className='botonesRow'>
            <button className='botonArrow' onClick={cambiarModoAtras}><IoIosArrowBack/></button>
            <p>Modo: {returnModoString(modo)}</p>
            <button className='botonArrow' onClick={cambiarModoAdelante}><IoIosArrowForward/></button>
          </div>

          <div className='botonesRow'>
            <button className='botonArrow' onClick={restarCantidadDeNumeros}><IoIosArrowBack/></button>
            <p>Cantidad de números: {cantidadNumeros}</p>
            <button className='botonArrow' onClick={sumarCantidadDeNumeros}><IoIosArrowForward/></button>
          </div>
        </div>        
      </div>

      <div className='display-2-columnas'>
        <form>
          {
            Array.from({ length: cantidadNumeros }).map((_, index) => (
              <InputLabel key={index+1} id={index+1} onChange={handleNumeroChange} />
            ))
          }          
        </form>
        <div>
          <div className='displayResultado '>
            {resultado !== null && 
              <>
                <p className='blueText'>Resultado: </p>
                <h2>{resultado}</h2>
              </>
            }
          </div>
          <button onClick={manageOperacion} className='botonArrow botonEjecutar'>{returnModoString(modo)}</button>
        </div>    
      </div>
            
      <div className="historialContainer">
        <h3>Historial de Operaciones</h3>
        <p style={{marginBottom:"0.5rem"}}>Opciones de filtro</p>
        <div className='botonesContainer'>
          <div className='divFiltro'>
            <label className='blueLabel'>Filtrar por tipo de operación</label>
            <select className='inputFiltro' onChange={(e) => dispatch({ type: "SET_OPERACION", payload: e.target.value })}>
              <option value="todos">Todos</option>
              <option value="suma">Suma</option>
              <option value="resta">Resta</option>
              <option value="multiplicacion">Multiplicación</option>
              <option value="division">División</option>
            </select>
          </div>

          <div className='divFiltro'>
            <label className='blueLabel'>Filtrar por fecha</label>
            <input type="date" className='inputFiltro' onChange={(e) => dispatch({ type: "SET_FECHA", payload: e.target.value })}/>
          </div>

          <div className='divFiltro'>
            <label className='blueLabel'>Ordenar por:</label>
            <select className='inputFiltro' onChange={(e) => dispatch({ type: "SET_ORDENAR", payload: e.target.value })}>
              <option value="ninguno">Ninguno</option>
              <option value="date">Fecha</option>
              <option value="resultado">Resultado</option>
            </select>
          </div>

          <div className='divFiltro'>
            <label className='blueLabel'>Orden:</label>
            <select className='inputFiltro' onChange={(e) => dispatch({ type: "SET_ORDEN", payload: e.target.value })}>
              <option value="asc">Ascendente</option>
              <option value="desc">Descendente</option>
            </select>
          </div>
          
        </div>
        <ul className="historialList">
          {historial.map((op, i) => (
            <li key={i} className="historialItem">
              <div className="historialInfo">
                <div className="historialDate">
                  {new Date(op.date).toLocaleString()}
                </div>
                <div className="historialOperation">
                  <p>{formatOperation(op)}</p>
                </div>
              </div>
              <div className="historialType">{op.operacion}</div>
            </li>
          ))}
        </ul>
      </div>
      
    </div>
  );
}

export default App;
