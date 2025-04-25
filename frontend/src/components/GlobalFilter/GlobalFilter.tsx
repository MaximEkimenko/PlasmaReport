import { Button, TextField } from "@mui/material";
import React, { useState } from "react";
import { GridRowModel } from "@mui/x-data-grid";
import { filterRows, syncFiltered } from "../../utils/handleGlobalfilter";

type FilterPropsType = {
    rows: GridRowModel[]; // инзначальные данные
    setRows: React.Dispatch<React.SetStateAction<GridRowModel[]>>;
    filteredRows: GridRowModel[]; // отфильтрованные данные
    setFilteredRows: React.Dispatch<React.SetStateAction<GridRowModel[]>>;
};

const GlobalFilter = ({ rows, setRows, filteredRows, setFilteredRows }: FilterPropsType) => {
    const [filterText, setFilterText] = useState("");

    const applyFilter = (filterText: string) => setFilteredRows(filterRows(rows, filterText));

    /**
     * сброс фильтра. Во время сброса отфильтрованные данные синхронизируются с оригинадьными
     */
    const clearFilter = () => {
        setFilterText("");
        applyFilter("");
        syncFiltered(filteredRows, setRows)
    };

    return (
        <>
            <TextField
                sx={{flex:1}}
                placeholder="поиск по всей таблице"
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
            />
            <Button variant="outlined" onClick={() => applyFilter(filterText)}>
                Найти
            </Button>
            <Button variant="outlined" color="error" onClick={clearFilter}>
                сбросить
            </Button>
        </>
    );
};
export default GlobalFilter;
