"""Сырые запросы в sigma nest."""
initial_table = "PartWithQtyInProcess"  # основная таблица справочно
joined_table = "WorkOrderWithPartQuantities"  # присоединённая справочно

# запрос на данные в интервале
main_query = """
            SELECT
            PartName,
            OrderDate,
            DateCreated,
            Cuttingtime,
            Material,
            Thickness,
            NetArea,
            Netweight,
            RectArea,
            RectWeight,
            QtyRemaining,
            WODate,
            dbo.WorkOrderWithPartQuantities.QtyCompleted,
            dbo.WorkOrderWithPartQuantities.QtyInProcess,
            dbo.WorkOrderWithPartQuantities.QtyOrdered,
            dbo.WorkOrderWithPartQuantities.WONumber
            FROM dbo.PartWithQtyInProcess
            INNER JOIN dbo.WorkOrderWithPartQuantities
            ON dbo.PartWithQtyInProcess.WONumber=dbo.WorkOrderWithPartQuantities.WONumber
            WHERE OrderDate > ? --start_date
            AND OrderDate < ? --end_date
            ORDER BY DateCreated
            """

# запрос на получение списка колонок
column_query = """
            SELECT
            PartName,
            OrderDate,
            DateCreated,
            Cuttingtime,
            Material,
            Thickness,
            NetArea,
            Netweight,
            RectArea,
            RectWeight,
            QtyRemaining,
            WODate,
            dbo.WorkOrderWithPartQuantities.QtyCompleted,
            dbo.WorkOrderWithPartQuantities.QtyInProcess,
            dbo.WorkOrderWithPartQuantities.QtyOrdered,
            dbo.WorkOrderWithPartQuantities.WONumber
            FROM dbo.PartWithQtyInProcess
            INNER JOIN dbo.WorkOrderWithPartQuantities
            ON dbo.PartWithQtyInProcess.WONumber=dbo.WorkOrderWithPartQuantities.WONumber
            ORDER BY DateCreated DESC
            """

# custom_query
custom_query = """


"""
