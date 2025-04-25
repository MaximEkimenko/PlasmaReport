import { configureStore } from "@reduxjs/toolkit";
import dateDiapazonSliceReducer from "./date_diapazon.slice";

export const store = configureStore({
    reducer: {diapazon: dateDiapazonSliceReducer},
});

export type RootState = ReturnType<typeof store.getState>;
export type AddDispatch = typeof store.dispatch;
