class UserBankAccount(models.Model):
    user = models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_TYPE)
    initial_deposite_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    def __str__(self):
        return str(self.account_no)

    def transfer(self, target_account_no, amount):
        # Check if the amount is valid
        if amount <= 0:
            raise ValidationError("The transfer amount must be greater than zero.")
        if self.balance < amount:
            raise ValidationError("Insufficient balance. The bank is bankrupt.")

        try:
            target_account = UserBankAccount.objects.get(account_no=target_account_no)
        except ObjectDoesNotExist:
            raise ValidationError(f"Account with number {target_account_no} does not exist.")
        self.balance -= amount
        target_account.balance += amount

        self.save()
        target_account.save()
        
        self.send_transfer_email(target_account, amount)

        return f"Transfer successful. {amount} has been transferred to account {target_account_no}."

    def send_transfer_email(self, target_account, amount):
        sender_email = self.user.email
        receiver_email = target_account.user.email

        send_mail(
            'Transaction Notification',
            f'You have successfully transferred {amount} to account {target_account.account_no}.',
            'ihanik.ad@example.com',
            [sender_email],
            fail_silently=False,
        )

        send_mail(
            'Transaction Notification',
            f'You have received {amount} from account {self.account_no}.',
            'ihanik.ad@example.com',
            [receiver_email],
            fail_silently=False,
        )
