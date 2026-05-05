from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "Newtimeline2026"
hashed = pwd_context.hash(password)

print("\nYOUR HASH:\n")
print(hashed)