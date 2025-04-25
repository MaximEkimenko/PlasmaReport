import { ICreateData, TechResponseType } from "../pages/Techman/Techman.types";
import { MasterResponseType } from "./requests.types";
import { LogistResponseType } from "./requests.types";
import { OperatorResponseType } from "./requests.types";

import { urls } from "./urls";

import { MasterProgramPartsRecordType } from "../pages/LogistTable/LogistTable.types";
import { ResponsePartsType } from "./requests.types";
import { AssignProgramRequestType, DoerType } from "../pages/Master/Master.types";
import { UserType } from "../pages/Login/Login.types";
import { apiClient } from "./axiosSetup";

/**
 * Записывает новые программы для резки в нашу базу
 * @param params
 */
export const userRegister = async (params) => {
    try {
        // Отправка POST-запроса на сервер с использованием axios
        const response = await apiClient.post(urls.AUTH_REGISTER, params);
        console.log("Ответ сервера: ", response);
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при содании нового пользователя:", error);
        return Promise.reject(error);
    }
};

/**
 * Получаем программы из плазмы за определенный период
 * @param dates
 * @returns
 */
export const getNewPrograms = async (dates: { start_date: string; end_date: string }) => {
    console.log("Запрос программ и работников");
    try {
        const { data } = await apiClient.get<TechResponseType>(urls.TECHMAN_GET_PROGRAMS, { params: dates });
        return data;
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе программ для добавления в базу:", error);
        return Promise.reject(error);
    }
};

export const getOrders = async (dates: { start_date: string; end_date: string }) => {
    try {
        const { data } = await apiClient.get<TechResponseType>(urls.TECHMAN_GET_ORDERS, { params: dates });
        return data;
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе программ для добавления в базу:", error);
        return Promise.reject(error);
    }
};

export const getOrderDetails = async (order: {wo_number: string}) => {
    try {
        const { data } = await apiClient.get<TechResponseType>(urls.ORDER_GET_WO_DETAILS, {params: order}  );
        return data;
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе деталей заказа:", error);
        return Promise.reject(error);
    }
};



/**
 * Получаем детали конкретной програмы из плазмы
 * @param programName
 * @returns
 */
export const getProgramParts = async (programName: string) => {
    console.log("Запрос программ и работников");
    try {
        const { data } = await apiClient.get<ResponsePartsType>(`${urls.TECHMAN_GET_PROGRAM_PARTS}/${programName}`);
        return data;
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе программ для добавления в базу:", error);
        return Promise.reject(error);
    }
};

/**
 * Записывает новые программы для резки в нашу базу
 * @param params
 */
export const techmanCreateData = async (params: ICreateData[]) => {
    try {
        // Отправка POST-запроса на сервер с использованием axios
        const response = await apiClient.post(urls.TECHMAN_CREATE_PROGRAM_DATA, params);
        console.log("Ответ сервера: ", response);
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе на создание программ:", error);
        return Promise.reject(error);
    }
};

export const techmanUpdateData = async (params: ICreateData[]) => {
    try {
        // Отправка POST-запроса на сервер с использованием axios
        const response = await apiClient.put(urls.TECHMAN_UPDATE_PROGRAM_DATA, params);
        console.log("Ответ сервера: ", response);
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе на обновление программ:", error);
        return Promise.reject(error);
    }
};

export const assignProgramsRequest = async (params: AssignProgramRequestType[]) => {
    try {
        await apiClient.post(urls.MASTER_ASSIGN_PROGRAMS, params);
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе на создание программ:", error);
    }
};

/**
 * Запрос получает список программ, готовых к распределению и список работников
 */
export const getProgramsAndDoers = async () => {
    console.log("Запрос программ и работников");
    try {
        const { data } = await apiClient.get<MasterResponseType>(urls.MASTER_GET_PROGRAMS_AND_DOERS);
        return data;
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе программ для распределения:", error);
    }
};

export const getDoers = async () => {
    try {
        const { data } = await apiClient.get<DoerType[]>(urls.MASTER_GET_DOERS);
        return data;
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе работников:", error);
    }
};

export const logistGetPrograms = async () => {
    try {
        const { data } = await apiClient.get<LogistResponseType>(urls.LOGIST_GET_PROGRAMS);
        return data;
    } catch (error) {
        console.error("Error fetching protected data:", error);
        return;
    }
};

export const masterGetDetailsByProgramId = async (program_id: Array<string>, fio_doer_id?: number) => {
    try {
        const { data } = await apiClient.get<ResponsePartsType>(urls.MASTER_GET_PARTS_BY_PROGRAM_ID, {
            params: { program_id, fio_doer_id },
        });
        //console.log(data);
        return data;
    } catch (error) {
        console.error("Ошибка получения деталей по идентификатору программы:", error);
        return;
    }
};

export const logistCalculateParts: (params: Array<{ id: number; qty_fact: number }>) => Promise<void> = async (
    params
) => {
    try {
        const result = await apiClient.post(urls.LOGIST_CALCULATE_PARTS, params);
        console.log(result);
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при отправке фактического количества деталей:", error);
    }
};

export const getPartsByStatuses = async () => {
    const params = { include_program_statuses: ["создана", "распределена"] };
    try {
        const { data } = await apiClient.get<MasterProgramPartsRecordType[]>(urls.MASTER_GET_PARTS_BY_STATUSES, {
            params: params,
        });
        return data;
    } catch (error) {
        console.error("Ошибка получения деталей по идентификатору программы:", error);
        return;
    }
};

export const getMyPrograms = async (fio_id: number) => {
    try {
        const { data } = await apiClient.get<OperatorResponseType>(urls.OPERATOR_GET_MY_PROGRAMS, {
            params: { fio_id },
        });
        return data;
    } catch (error) {
        console.error("Ошибка получения программ по идентификатору исполнителя:", error);
        return;
    }
};

export const OperatorStartProgram = async (program_id: number, new_status?: string) => {
    try {
        const { data } = await apiClient.get<{ msg: string }>(urls.OPERATOR_START_PROGRAM, {
            params: { program_id, new_status },
        });
        return data;
    } catch (error) {
        console.error("Ошибка при изменении статуса программы:", error);
        return;
    }
};

export const OperatorSetMyPrograms = async (params: {
    program_id: number;
    fio_doer_id: number;
    parts_ids: number[];
}) => {
    console.log(JSON.stringify(params));
    try {
        await apiClient.post(urls.OPERATOR_SET_MY_PARTS, params);
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при присвоении деталей оператору:", error);
    }
};

export const getCurrentUser = async () => {
    try {
        const { data } = await apiClient.get<UserType>(urls.USER_ME);
        return data;
    } catch (error) {
        return Promise.reject(error);
    }
};

export const logout = async () => {
    try {
        const response = await apiClient.post(urls.AUTH_LOGOUT, "");
        return response;
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при логауте:", error);
    }
};

/**
 * Получаем данные для отчета за определенный период
 * @param dates
 * @returns
 */
export const getReportData = async (dates: { start_date: string; end_date: string }) => {
    try {
        const { data } = await apiClient.get<ResponsePartsType>(urls.REPORT_PARTS_FULL, { params: dates });
        return data;
    } catch (error) {
        if (error instanceof Error) console.error("Ошибка при запросе отсета за период:", error);
        return Promise.reject(error);
    }
};
