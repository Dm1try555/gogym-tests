class TrainingPackagesEndpoints:

    CREATE_TRAINING_PACKAGE = "/trainings/sports/{sport}"

    BUY_PACKAGE = "/training-packages/buy"
    REFUND_PACKAGE = "/training-packages/refund"
    AVAILABLE_TO_BUY = "/training-packages/customer/available-to-buy"

    @staticmethod
    def delete_package(package_id: int) -> str:
        return f"/training-packages/{package_id}"