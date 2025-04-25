import { StrictMode, lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";

import "./index.css";
import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";

import { Provider } from "react-redux";
import { store } from "./store/store.ts";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
//локализация
import { ruRU } from "@mui/x-data-grid/locales";
import { ruRU as coreruRU } from "@mui/material/locale";
import { ruRU as dateruRU } from "@mui/x-date-pickers/locales";
import MasterContext from "./context.tsx";
import { setupInterceptors } from "./utils/axiosSetup.ts";

import { router } from "./routes";
import { BorderBottom } from "@mui/icons-material";

// import NewLogist from "./pages/Logist/Logist.tsx";
// import NewLogistTable from "./pages/Logist/LogistTable.tsx";

const theme = createTheme(
    {
        palette: {
            mode: "dark",
            primary: {
                main: "#e8e8d1",
                contrastText: "#060606",
                //dark: '#15a00f',
                dark: "#357EFF",
                light: "#f3f3d9",
            },
            secondary: {
                main: "#ec562d",
            },
            background: {
                default: "#3D3B38",
                paper: "#4a4747",
            },
            divider: "rgba(212,212,212,0.58)",
            text: {
                secondary: "rgba(209,209,209,0.9)",
                primary: "rgba(255,255,255,0.95)",
                disabled: "rgba(200,200,200,0.45)",
                hint: "#acacb7",
            },
        },
        components: {
            MuiDataGrid: {
                styleOverrides: {
                    root: {


                        "@media print": {
                            "--DataGrid-rowBorderColor": "transparent",
                            fontSize: "14px",
                            fontWieght: 300,
                            border: "1px solid black",
                            color: "black",

                            //"& .MuiDataGrid-root": { border: "none"},


                            ".MuiDataGrid-columnHeaders": {
                                //"--DataGrid-rowBorderColor": "red",
                            },
                            ".MuiDataGrid-columnHeaders": {
                                backgroundColor: "#E0E0E0",
                                "& .MuiDataGrid-filler": {
                                    backgroundColor: "#E0E0E0",
                                },
                            },


                            ".MuiDataGrid-columnHeader": {
                                backgroundColor: "#E0E0E0",
                            },

                            "& .MuiDataGrid-columnHeaderTitle": {
                                //fontSize:"12px",
                                wordBreak: "break-word",
                                overflow: "visible",
                                fontWeight: "normal",
                                whiteSpace: "wrap",
                            },

                            // ".MuiDataGrid-virtualScrollContent": { border: "2px dashed red" },
                            //".MuiDataGrid-virtualScroller": { border: "3px dotted brown", overflow: "visible" },

                            "& .MuiDataGrid-row": {
                                pageBreakInside: "avoid",
                                height: "auto",
                                //border: "1px dashed red",
                                borderBottom: "1px solid black",
                                overflow: "hidden",
                            },
                            // ".MuiDataGrid-row--lastVisible": {
                            //     border: "2px dotted cyan",
                            // },

                            ".MuiDataGrid-footerContainer": {
                                display: "none",
                            },
                            ".MuiDataGrid-toolbarContainer": {
                                display: "none",
                            },
                        },
                    },
                },
            },
        },
    },
    ruRU, // x-data-grid translations
    coreruRU, // core translations
    dateruRU // date-pickers
);

//если не запустить настройку запросов здесь, то не будут посылаться заголовки с токеном
// и нельзя будет получить пользователя после логина
setupInterceptors();

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <Provider store={store}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <MasterContext>
                    <RouterProvider router={router} future={{ v7_startTransition: true }} />
                </MasterContext>
            </ThemeProvider>
        </Provider>
    </StrictMode>
);
