export const convertDateToString = (date: Date | null): string => {
    if (date) {
        return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().split("T")[0];
    }
    return "";
};

export const convertStringToDate = (dateString: string): Date | null => {
    let date = null;
    if (dateString) {
        try {
            date = new Date(Date.parse(dateString));
        } catch (e) {
            if (e instanceof Error) {
                console.log( e.name, e.message);    
            }
            console.log("Неверный формат даты. Должен быть  YYYY-MM-DD.\n");
        }
    }
    return date;
};
