import { DataGrid, DataGridProps, GridRowModel, GridColDef } from "@mui/x-data-grid";
import { useState, memo, useEffect, useCallback, useRef } from "react";
import SearchToolbar, { SearchToolbarType } from "../CustomToolbar/SearchToolbar";
import { filterRows } from "../../utils/handleGlobalfilter";

export type FilterableDataGtidProps = Omit<DataGridProps, "rows" | "columns"> & {
    rows: GridRowModel[];
    //setRows: React.Dispatch<React.SetStateAction<GridRowModel[]>>;
    columns: GridColDef[];
};

const FilterableDataGtid = memo(({ rows, columns, ...props }: FilterableDataGtidProps) => {
    // rows и columns сохраняются в компонетне, а в таблицу отправляются filtered
    // если ячейки таблицы редактируются, то изменения вносятся в rows, а filteredRows 
    // просто отображают измененные оригинальные данные
    const [filteredRows, setFilteredRows] = useState<GridRowModel[]>(rows);
    const [filterText, setFilterText] = useState("");
    const prevFilterText = useRef(filterText);

    // фильтрует столбцы для таблицы
    const getFilteredData = useCallback(
        (filterText: string) => {
            setFilteredRows(filterRows(rows, filterText));
        },
        [rows]
    );

    // фильтрация по таблице происходит либо мгновенно, когда внутри таблицы меняются значения
    // либо с паузой, когра происходит ввод глобального фильтра, чтобы таблица не дергалась на каждое нажатие клавиши
    useEffect(() => {
        let timeout = 0;
        const changed = filterText !== prevFilterText.current
        if (changed) timeout = 500;
        const timeoutId = setTimeout(() => {
            getFilteredData(filterText);
            prevFilterText.current = filterText
        }, timeout);
        return () => {
            clearTimeout(timeoutId);
        };
    }, [filterText, getFilteredData]);


    return (
            <DataGrid
                rows={filteredRows}
                columns={columns}
                {...props}
                slots={{ toolbar: SearchToolbar }}
                slotProps={{ toolbar: { filterText, setFilterText } as SearchToolbarType }}
                getRowHeight={() => "auto"}
                
            />
    );
});
export default FilterableDataGtid;
