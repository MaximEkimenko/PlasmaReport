import { useEffect, useState, useCallback, useRef, useMemo } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Box, Typography } from "@mui/material";
import { GridColDef, useGridApiRef } from "@mui/x-data-grid";
import { DoerType } from "../../pages/Master/Master.types";
import { getProgramParts } from "../../utils/requests";
import { MasterProgramPartsRecordType } from "../LogistTable/LogistTable.types";
import { hiddenIdColumn } from "../../utils/tableInitialState";
import FilteredDataGrid from "../../components/FilterableDataGrid/FilterableDataGrid";
import { ImageWidget } from "../../components/IamgeWidget/ImageWidget";
import { BASE_URL } from "../../utils/urls";

const columnFields: string[] = [
    "id",
    "PartName",
    "WONumber",
    "part_pic",
    "PartLength",
    "PartWidth",

    //"WOData1",
    "QtyInProcess",
    //"qty_fact",
    //"Thickness",
    //"fio_doer",
];

const PlasmaParts = () => {
    // Состояние, которое передается при нажатии на сылку. Нужно для отображения имени программы в заголовке,
    // так как у деталей такой информции нет
    
    const addressParams = useParams()

    console.log("кусок пути:", addressParams.programName)
    const loc = useLocation();
    console.log("вся инфа по переходу", loc)

    const columns = useRef<GridColDef[]>([]);
    const [data, setData] = useState<MasterProgramPartsRecordType[]>([]);
    const apiRef = useGridApiRef();
    const [loadError, setLoadError] = useState(false);
    const [showTable, setShowTable] = useState(false);
    const programImg = useRef<string | null>(null)

    const prepareData = (data: MasterProgramPartsRecordType[]): MasterProgramPartsRecordType[] => {
        const processedData: MasterProgramPartsRecordType[] = data.map((item) => {
            const row = columnFields.reduce<MasterProgramPartsRecordType>((acc, field) => {
                acc[field] = item[field];
                return acc;
            }, {} as MasterProgramPartsRecordType);
            //////////////////////////
            // так быть не должно, нужно поле  id для деталей
            row["id"] = item.PK_PIP;
            row["part_pic"] = item.part_pic?`${BASE_URL}${item.part_pic}`: null;
            return row;
        });
        return processedData;
    };

    /** При загрузке страницы загружаем данные о деталях*/
    useEffect(() => {
        const loader = async () => {
            setShowTable(false);
            const response = await getProgramParts(addressParams.programName as string);
            if (response !== undefined) {
                setData(prepareData(response.data));
                columns.current = createColumns(response.headers);
                programImg.current = response.program_pic?`${BASE_URL}${response.program_pic}`: null;
                setLoadError(false);
                setShowTable(true);
            } else {
                setLoadError(true);
            }
        };

        loader();
    }, []);

    const createColumns = useCallback((headers: Record<string, string>) => {
        const clmns: GridColDef[] = columnFields.map((columnname) => {
            let col: GridColDef = {
                field: columnname,
                headerName: headers[columnname],
                flex: 1,
            };
            if (columnname == "fio_doers") {
                col = {
                    ...col,
                    valueGetter: (value: DoerType | DoerType[] ) => {
                        if (Array.isArray(value)) {
                            return value.map((item) => item.fio_doer).join(", ");
                        }
                        return value.fio_doer;
                    },
                };
            }
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
                <Typography variant="h5">
                    Информация о деталях программы № {addressParams.programName} на странице логиста
                </Typography>

                {loadError && <div>Ошибка загрузки</div>}
                {showTable && (
                    <>
                    <ImageWidget source={programImg.current}/>
                    <div style={{ height: 600, width: "100%" }}>
                        <FilteredDataGrid {...gridParams} />
                    </div>
                    </>
                )}
            </Box>
        </>
    );
};

export default PlasmaParts;
