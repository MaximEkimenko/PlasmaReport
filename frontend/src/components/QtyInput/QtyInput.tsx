import { TextField } from "@mui/material";
import React, { useEffect, useState } from "react";

type ChangeDataCallback = () => number;
type AssignData = {
    [key: string]: ChangeDataCallback;
};
type AssignHandlerType = (rowId: number, data: AssignData) => void;

type SetQtyType = {
    rowId: number;
    initialQty: number;
    assignHandler: AssignHandlerType;
};

export function QtyInput({ rowId, initialQty, assignHandler }: SetQtyType) {
    const [qty, setQty] = useState(initialQty);
    
    const hadleSetQty = (event: React.ChangeEvent<HTMLInputElement>) => {
        // если удалить из строки ввода всё, там появляется NaN, что приводит к ошибке
        // В этом случае нужно принудительно заменять NaN на 0
        const converted = Number.parseInt(event.target.value);
        const newValue = !isNaN(converted) ? converted : 0;
        setQty(newValue);
    };

    const updateTable = () => {
        if (qty !== initialQty) assignHandler(rowId, { qty_fact: () => qty });
    };

    // это не работает корректно, так как при нажатии на Enter курсор не перескакиевает в другую ячейку
    //а чтобы перескочить в другую ячпйку надо выскочить из поля ввода
    const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
        if (event.key === "Enter") {
            updateTable();
        }
    };

    useEffect(() => {
        setQty(initialQty);
    }, [initialQty]);

    return (
        <>
            <TextField
                size="small"
                sx={{ margin: 1 }}
                value={qty}
                onBlur={updateTable}
                onChange={hadleSetQty}
                onKeyDown={handleKeyDown}
                autoComplete="off"
            />
        </>
    );
}
