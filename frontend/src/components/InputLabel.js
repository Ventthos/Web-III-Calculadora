import { useState } from 'react'
export function InputLabel({id, onChange}){
    const [value, setValue] = useState(0);

    function onChangeValue(rawValue) {
        let newValue = Number(rawValue); 

        if (isNaN(newValue) || newValue < 0) {
            newValue = 0;
            setValue(0);
        } else {
            setValue(newValue);
        }

        onChange(id - 1, newValue);
    }


    return(
        <div className='inputLabel' key={id}>
            <label htmlFor={`numero${id}`}>Número {id}</label>
            <input
              type="number"
              onChange={(e) => onChangeValue(e.target.value)}
              placeholder={`Número ${id}`}
              name={`numero${id}`}
              id={`numero${id}`}
              min={0}
              value={value}
            />
        </div>
    )
}