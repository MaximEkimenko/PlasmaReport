import { Dayjs } from "dayjs";

export const enum ProgramStatus {
    NEW = "новая",
    CREATED = "создана",
}

export type TechProgramType = {
    id?: number;
    program_id: number | undefined
    ProgramName: string;
    program_status: ProgramStatus;
    UserName: string;
    PostDateTime: string;
    Material: string;
    program_pic: string
};

export type TechResponseType = {data: TechProgramType[], headers: Record<string, string>}

export type ProcessedPrognameType = TechProgramType & { id: string; checked: boolean };

export type DateDiapazonType = {
    startDate: Dayjs;
    endDate: Dayjs;
};

export type handleCreateDataType = (params: ICreateData[]) => void;
export type handleSelectType = (params: ICreateData) => void;

export interface ICreateData {
    program_status: ProgramStatus;
    ProgramName: string;
}
