import React from "react"
// код позаимствован из https://github.com/prettyblueberry/mui-datagrid-full-edit/blob/main/src/lib/components/GridExcelExportMenuItem.js
import { Button } from "@mui/material";
import * as XLSX from "xlsx";
import {
    GridColDef,
    gridFilteredSortedRowIdsSelector,
    gridVisibleColumnFieldsSelector,
    useGridApiContext,
} from "@mui/x-data-grid";
import { columnTypes } from "./reportColumnTypes";
import { GridApiCommunity } from "@mui/x-data-grid/internals";

function getExcelData(apiRef:React.RefObject<GridApiCommunity>) {
    // Select rows and columns
    const filteredSortedRowIds = gridFilteredSortedRowIdsSelector(apiRef);
    const visibleColumnsField = gridVisibleColumnFieldsSelector(apiRef);
    // Format the data. Here we only keep the value
    return filteredSortedRowIds.map((id) => {
        const row = {};
        visibleColumnsField.forEach((field) => {
            row[field] = apiRef.current.getCellParams(id, field).value;
        });
        return row;
    });
}

function handleExport(apiRef:React.RefObject<GridApiCommunity>, columns: GridColDef[], filename: string) {
    const data = getExcelData(apiRef);
    const fields = Object.keys(data[0]);
    const translateObj = columns.reduce((acc, item) => {
        acc[item.field] = item.headerName;
        return acc;
    }, {} as Record<string, string | undefined>);

    const rows = data.map((row) => {
        const mRow = {};
        for (const key of fields) {
            // значение и тип ячейки (сейчас строка либо число)
            mRow[key] = { v: row[key]? row[key]: "", t: columnTypes[key] };
            // if (["time_program_started", "time_program_finished"].includes(key)) {
            //     mRow[key] = {...mRow[key],  v: ""};
            //}
        }


        return mRow;
    });

    const columnNames = fields.map((item) => translateObj[item]);
    const worksheet = XLSX.utils.json_to_sheet(rows);
    XLSX.utils.sheet_add_aoa(worksheet, [[...columnNames]], {
        origin: "A1",
    });

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Лист1");
    console.log(workbook, filename);

    XLSX.writeFile(workbook, filename, { compression: true });
}

type ExportType = { columns:GridColDef[], filename:string }

export default function GridExcelExportMenuItem({ columns, filename }: ExportType) {
    const apiRef = useGridApiContext();
    return (
        <Button
            variant="contained"
            size="small"
            onClick={() => {
                handleExport(apiRef, columns, filename);
            }}
        >
            Скачать XLSX
        </Button>
    );
}
