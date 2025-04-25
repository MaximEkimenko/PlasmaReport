import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface IDateDiapazon {
    startDate: string;
    endDate: string;
}

const initialState: IDateDiapazon = { startDate: "", endDate: "" };

export const dateDiapazonSlice = createSlice({
    name: "diapazon",
    initialState,
    reducers: {
        setDiapazon: (state, action: PayloadAction<IDateDiapazon>) => {
            state.startDate = action.payload.startDate;
            state.endDate = action.payload.endDate;
        },
    },
});

export default dateDiapazonSlice.reducer;
export const dateDiapazonActions = dateDiapazonSlice.actions;
