import { useState, useEffect, useRef, useCallback } from "react";
import { Box, Typography, Button, Stack, Checkbox } from "@mui/material";
import { DataGrid, GridColDef, useGridApiRef, GridColumnVisibilityModel, GridRowModel } from "@mui/x-data-grid";

import { getOrderDetails, getReportData } from "../../utils/requests";
import { ProgramType } from "../Master/Master.types";
import { hiddenIdColumn } from "../../utils/tableInitialState";
import { MasterProgramPartsRecordType } from "../LogistTable/LogistTable.types";

import ReportToolbar from "../../components/CustomToolbar/ReportToolbar";

import axios from "axios";
import { getVisibilityModelToStore, saveVisibilityModelToStore } from "../../utils/local-storage";
import { useLocation } from "react-router-dom";

export type ProgramAndFioType = ProgramType & { dimensions: string };

const VISIBILITY_MODEL_STORAGE_KEY = "order_detail_report_visibility"

export function OrderDetails() {
    const { state } = useLocation();

    const [data, setData] = useState<MasterProgramPartsRecordType[]>([]);
    const [loadError, setLoadError] = useState(false);
    const [showTable, setShowTable] = useState(false);
    const [columnVisibilityModel, setColumnVisibilityModel] = useState(getVisibilityModelToStore(VISIBILITY_MODEL_STORAGE_KEY));

    const columns = useRef<GridColDef[]>([]);

    const errorMessage = useRef("Ошибка загрузки");
    const createColumns = useCallback((headers: Record<string, string>) => {
        const columns: GridColDef[] = Object.keys(headers).map((columnname) => {
            const colTemplate: GridColDef = {
                field: columnname,
                headerName: headers[columnname],
                width: 160,
            };

            return colTemplate;
        });
        return columns;
    }, []);

    const prepareData = (rawData) =>{
        const prepared = rawData.map((item, index)=> ({...item, id:index}))
        return prepared
    }

    const loader = async () => {
        setShowTable(false);
        try {
            const response = await getOrderDetails({wo_number: state.WONumber});
            if (response !== undefined) {
                
                setData(prepareData(response.data));
                columns.current = createColumns(response.headers);
                setShowTable(true);
                setLoadError(false);
            } else {
                setLoadError(true);
            }
        } catch (error) {
            errorMessage.current = "Ошибка загрузки";
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 404) {
                    errorMessage.current = "Отсутствуют записи за выбранный период";
                }
            }
            setLoadError(true);
        }
    };

    useEffect(() => {
        loader();
    }, []);


    useEffect(() => console.log(columnVisibilityModel), [columnVisibilityModel]);
    const handleVisibilityModel = (newModel: GridColumnVisibilityModel) => {
        setColumnVisibilityModel(newModel);
        saveVisibilityModelToStore(newModel, VISIBILITY_MODEL_STORAGE_KEY);
    };

    const getFilname = () => {
        return `детали заказа ${state.WONumber}.xlsx`;
    };



    return (
        <>
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, mt: 1 }}>
                <Typography variant="h5">Отчет по заказу {state.WONumber}</Typography>
                {loadError && <div>{errorMessage.current}</div>}

                {showTable && (
                    <div style={{ height: 700, width: "100%" }}>
                        <DataGrid
                            rows={data}
                            columns={columns.current}
                            slots={{ toolbar: ReportToolbar }}
                            slotProps={{ toolbar: { columns: columns.current, filename: getFilname() } }}
                            initialState={hiddenIdColumn}
                            getRowHeight={() => "auto"}
                            columnVisibilityModel={columnVisibilityModel}
                            onColumnVisibilityModelChange={handleVisibilityModel}
                        />
                    </div>
                )}
            </Box>
        </>
    );
}
