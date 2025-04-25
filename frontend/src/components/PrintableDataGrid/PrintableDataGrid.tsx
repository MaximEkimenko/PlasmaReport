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
    tableRef: React.Ref<HTMLDivElement>;
    initialState: GridInitialState;
};

export const PrintableDataGrid = memo(
    ({ rows, columns, tableRef, initialState, ...props }: FilterableDataGtidProps) => {
        const [filteredRows, setFilteredRows] = useState<GridRowModel[]>(rows);
        const [filterText, setFilterText] = useState("");
        // const tableHeigth = useRef(600); //высота таблицы по умолчанию

        const  [tableHeigth, setTableHeigth] = useState(600)
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
        useEffect(
            () => {
                let total = 0
                const printableRows = document.querySelectorAll("#printalbe-table .MuiDataGrid-row")
                console.log("количество столбцов", printableRows.length)
                printableRows.forEach((row)=> total += row.clientHeight)
                setTableHeigth(total + 140)
                console.log("общая длина", tableHeigth)
                // tableHeigth.current = 145 + filteredRows.length * 145;
            },
            [filteredRows]
        );

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
            <>
                <div style={{ height: 600, width: "100%" }}>
                    <DataGrid
                        rows={filteredRows}
                        columns={columns}
                        {...props}
                        slots={{ toolbar: SearchToolbar }}
                        slotProps={{ toolbar: { filterText, setFilterText } as SearchToolbarType }}
                        getRowHeight={() => "auto"}
                        columnVisibilityModel={columnVisibilityModel}
                        onColumnVisibilityModelChange={handleVisibilityModel}
                        filterModel={filterModel}
                        onFilterModelChange={(newFilterModel) => setFilterModel(newFilterModel)}
                    />
                </div>
                <div id = "printalbe-table"
                    ref={tableRef}
                    // высота таблицы нужна обязательно, иначе обрезает строки
                    style={{ height: tableHeigth, width: "1306px" }}
                    className={styles["print-container"]}
                >
                    {/* <Typography variant="h5"  sx={{color:"black"}}>Вот так ведомость! Что за ведомость!</Typography>
                    <Typography variant="body1" sx={{color:"black"}}>В категории приложений самыми скачиваемыми оказались мобильные решения «ВКонтакте», «Халва — Совкомбанк», «VK Видео», «Ozon Банк» и «СберKids». Причём в топе по скачиваниям произошли изменения, например, приложение «РЖД Пассажирам: билеты на поезд» обогнало сервис покупки авиабилетов «Аэрофлот».</Typography> */}
                    <DataGrid 
                        //sx ={{border: "none"}}
                        rows={filteredRows}
                        columns={columns}
                        className={styles["print-table"]}
                        {...props}
                        getRowHeight={() => "auto"}
                        disableVirtualization
                        columnVisibilityModel={columnVisibilityModel}
                        filterModel={filterModel}
                    />
                </div>
            </>
        );
    }
);
