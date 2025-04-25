import {
    DataGrid,
    DataGridProps,
    GridRowModel,
    GridColDef,
    GridColumnVisibilityModel,
    GridInitialState,
    GridFilterModel,
} from "@mui/x-data-grid";
import React, { useState, memo, useEffect, useCallback, useRef } from "react";
import SearchToolbar, { SearchToolbarType } from "../CustomToolbar/SearchToolbar";
import { filterRows } from "../../utils/handleGlobalfilter";
import styles from "./PritableDataGrid.module.css";

export type FilterableDataGtidProps = Omit<DataGridProps, "rows" | "columns"> & {
    rows: GridRowModel[];
    columns: GridColDef[];
    initialState: GridInitialState;
};

export const SinglePrintableDataGrid = memo(
    ({ rows, columns, tableRef, initialState, ...props }: FilterableDataGtidProps) => {
        const [filteredRows, setFilteredRows] = useState<GridRowModel[]>(rows);
        const [filterText, setFilterText] = useState("");
        // const tableHeigth = useRef(600); //высота таблицы по умолчанию

        const [tableHeigth, setTableHeigth] = useState(600);
        const prevFilterText = useRef(filterText);
        const [columnVisibilityModel, setColumnVisibilityModel] = useState<GridColumnVisibilityModel>(
            initialState.columns?.columnVisibilityModel
        );
        const [filterModel, setFilterModel] = React.useState<GridFilterModel>({
            items: [
                {
                    field: "",
                    operator: "",
                    value: "",
                },
            ],
        });

        // для принудительной перерисовки экрана
        const [, setTick] = useState(0);
        // Функция для вызова рендера обновляет состояние
        const forceUpdate = () => setTick(tick => tick + 1);



        // фильтрует столбцы для таблицы
        const getFilteredData = useCallback(
            (filterText: string) => {
                setFilteredRows(filterRows(rows, filterText));
            },
            [rows]
        );

        const handleVisibilityModel = (newModel: GridColumnVisibilityModel) => {
            setColumnVisibilityModel(newModel);
        };

        // подгонка размера таблицы для печати под актуальные данные
        useEffect(() => {
            console.log(filterModel);
            const rowHeights = []
            let total = 145;
            const printableRows = document.querySelectorAll("#printalbe-table .MuiDataGrid-row");
            console.log("количество столбцов", printableRows.length);
            printableRows.forEach((row) => {
                rowHeights.push(row.clientHeight)
                total += row.clientHeight
            });
            total +=  140*Math.floor(printableRows.length /15)
            console.log(rowHeights)
            setTableHeigth(total );
            console.log("общая длина", total);
            forceUpdate()
        }, [filterModel, filteredRows]);

        // фильтрация по таблице происходит либо мгновенно, когда внутри таблицы меняются значения
        // либо с паузой, когра происходит ввод глобального фильтра, чтобы таблица не дергалась на каждое нажатие клавиши
        useEffect(() => {
            let timeout = 0;
            const changed = filterText !== prevFilterText.current;
            if (changed) timeout = 500;
            const timeoutId = setTimeout(() => {
                getFilteredData(filterText);
                prevFilterText.current = filterText;
            }, timeout);
            return () => {
                clearTimeout(timeoutId);
            };
        }, [filterText, getFilteredData]);

        return (
            <div id="printalbe-table">
                <DataGrid
                    style={{ height: tableHeigth, width: "1306px" }}
                    rows={filteredRows}
                    columns={columns}
                    className={styles["print-table"]}
                    slots={{ toolbar: SearchToolbar }}
                    slotProps={{ toolbar: { filterText, setFilterText } as SearchToolbarType }}
                    {...props}
                    getRowHeight={() => "auto"}
                    disableVirtualization
                    columnVisibilityModel={columnVisibilityModel}
                    filterModel={filterModel}
                    onFilterModelChange={(newFilterModel) => setFilterModel(newFilterModel)}
                />
            </div>
        );
    }
);
