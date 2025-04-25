import React, { useState, createContext, ReactNode } from "react";
import { DateDiapazonType } from "./pages/Techman/Techman.types";
import dayjs from "dayjs";
import { AuthProvider } from "./AuthContext";

export type DateDiapazonContextType = {
    dateDiapazon: DateDiapazonType;
    setDateDiapazon: React.Dispatch<React.SetStateAction<DateDiapazonType>>;
};

type OperatorSelectContextType = {
    selectedOperatorId: number | undefined;
    setSelectedOperatorId: (arg: number) => void;
};

const defaultDates: DateDiapazonType = {
    startDate: dayjs().subtract(7, "day"),
    endDate: dayjs(),
};

export const ReportDateDiapazonContext = createContext<DateDiapazonContextType | undefined>(undefined);
export const DateDiapazonContext = createContext<DateDiapazonContextType | undefined>(undefined);
export const OperatorSelectContext = createContext<OperatorSelectContextType | undefined>(undefined);

type MasterContextProps = { children: ReactNode };

const MasterContext = ({ children }: MasterContextProps) => {
    const [dateDiapazon, setDateDiapazon] = useState<DateDiapazonType>(defaultDates);
    const [reportDateDiapazon, setReportDateDiapazon] = useState<DateDiapazonType>(defaultDates);
    const [selectedOperatorId, setSelectedOperatorId] = useState<number | undefined>(undefined);

    return (
        <>
            <AuthProvider>
            <ReportDateDiapazonContext.Provider value={{ dateDiapazon, setDateDiapazon }}>
                <DateDiapazonContext.Provider value={{ dateDiapazon:reportDateDiapazon, setDateDiapazon:setReportDateDiapazon }}>
                    <OperatorSelectContext.Provider
                        value={{ selectedOperatorId: selectedOperatorId, setSelectedOperatorId }}
                    >
                        {children}
                    </OperatorSelectContext.Provider>
                </DateDiapazonContext.Provider>
                </ReportDateDiapazonContext.Provider>
            </AuthProvider>
        </>
    );
};

export default MasterContext;
