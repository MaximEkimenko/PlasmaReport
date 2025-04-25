import { ProgramPriorityType, LogistProgramType } from "../Logist/Logist.types";

export type ProgramType = LogistProgramType & { fio_doers: DoerType[] };

export type DoerType = {
    fio_doer: string;
    position: string;
    is_active: boolean;
    user_id: number;
    id: number;
    created_at?: string;
    updated_at?: string;
};

export type ProgramExtendedType = ProgramType & { doerIds: number[]; doerFio: string; };

export type AssignProgramRequestType = {
    id: number;
    fio_doers_ids?: Array<number>;
    program_priority?: ProgramPriorityType;
};

export type OrderReportType = {
            WONumber: string;
            CustomerName: string;
            WODate: string;
            OrderDate: string;
            WOData1: string;
            WOData2: string;
            DateCreated: string;
}


//показывает, какще из полей в таблице мастера повергается изменению
export type changeFieldType = "program_priority" | "doerIds";
