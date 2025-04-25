import { useEffect, useState, useCallback, useRef, useMemo } from "react";
import { useLocation, useParams } from "react-router-dom";

import { Box, Typography } from "@mui/material";
import { GridColDef, useGridApiRef } from "@mui/x-data-grid";
import { ProgramExtendedType } from "../Master/Master.types";

import { masterGetDetailsByProgramId } from "../../utils/requests";
import FilteredDataGrid from "../../components/FilterableDataGrid/FilterableDataGrid";
import { MasterProgramPartsRecordType } from "../LogistTable/LogistTable.types";
import { hiddenIdColumn } from "../../utils/tableInitialState";
import { BASE_URL } from "../../utils/urls";
import { ImageWidget } from "../../components/IamgeWidget/ImageWidget";
import { useProgramInfo } from "../../hooks";

const columnFields: (keyof MasterProgramPartsRecordType)[] = [
    //обязательно нужен id
    "PartName",
    "WONumber",
    "part_pic",
    "PartLength",
    "PartWidth",
    "WOData1",
    "QtyInProcess",
    "qty_fact",
    "Thickness",
    "fio_doers",
];

const PartsList = () => {
    const programInfo =  useProgramInfo()

    const columns = useRef<GridColDef[]>([]);
    const [data, setData] = useState<MasterProgramPartsRecordType[]>([]);
    const apiRef = useGridApiRef();
    const [loadError, setLoadError] = useState(false);
    const [showTable, setShowTable] = useState(false);
    const programImg = useRef<string | null>(null)
    const prepareData = (data: MasterProgramPartsRecordType[]) => {
        const processedData = data.map((item) => {
            const row = columnFields.reduce<MasterProgramPartsRecordType>((acc, field) => {
                acc[field] = item[field];
                return acc;
            }, {});
            row["part_pic"] = item.part_pic?`${BASE_URL}${item.part_pic}`: null;
            row["fio_doers"] = item.fio_doers.map((item) => item.fio_doer).join(", ");
            //////////////////////////
            // так быть не должно, нужно поле  id для деталей
            row["id"] = item.PK_PIP;
            return row;
        });
        return processedData;
    };

    const createColumns = useCallback((headers) => {
        const clmns: GridColDef[] = columnFields.map((columnname) => {
            let col: GridColDef = {
                field: columnname,
                headerName: headers[columnname],
                flex: 1,
            };
            if (columnname === "part_pic") {
                col = {
                    ...col,
                    width: 130,
                    flex: 0,
                    renderCell: (params) => <ImageWidget source={params.value} />,
                };
            }
            
            return col;
        });
        return clmns;
    }, []);

    /*Функция загрузки данных о деталях */
    const loader = useCallback( async () => {
        setShowTable(false);
        const response = await masterGetDetailsByProgramId(programInfo.programIds);
        if (response !== undefined) {
            console.log(response)
            setData(prepareData(response.data));
            columns.current = createColumns(response.headers);
            programImg.current = response.program_pic?`${BASE_URL}${response.program_pic}`: null;
            setShowTable(true);
            setLoadError(false);
        } else {
            setLoadError(true);
        }
    }, [createColumns])

    /** При загрузке страницы загружаем данные о деталях*/
    useEffect(() => {
        loader();
    }, [loader]);

    const gridParams = useMemo(
        () => ({
            rows: data,
            setRows: setData,
            columns: columns.current,
            initialState: hiddenIdColumn,
            apiRef: apiRef,
        }),
        [apiRef, data]
    );

    return (
        <>
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, mt: 1 }}>
                <Typography variant="h5">Информация о деталях программы № {programInfo.programName}</Typography>
                
                {loadError && <div>Ошибка загрузки</div>}
                {showTable && (
                    <>
                    <ImageWidget source={programImg.current}/>
                        <div style={{ height: 700, width: "100%" }}>
                            <FilteredDataGrid {...gridParams} />
                        </div>
                    </>
                )}
            </Box>
        </>
    );
};

export default PartsList;
