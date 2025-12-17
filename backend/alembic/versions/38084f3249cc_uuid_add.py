"""uuid add

Revision ID: 38084f3249cc
Revises: eb6d6bd45e7e
Create Date: 2025-10-31 21:31:37.505261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38084f3249cc'
down_revision: Union[str, Sequence[str], None] = 'eb6d6bd45e7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to use UUIDs instead of integers."""
    # Enable uuid-ossp extension for UUID generation
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    
    # Drop foreign key constraints first
    op.drop_constraint('transaction_sender_id_fkey', 'transaction', type_='foreignkey')
    op.drop_constraint('transaction_receiver_id_fkey', 'transaction', type_='foreignkey')
    op.drop_constraint('fraudalert_user_id_fkey', 'fraudalert', type_='foreignkey')
    
    # Add new UUID columns
    op.add_column('user', sa.Column('new_id', sa.Uuid(), nullable=True))
    op.add_column('transaction', sa.Column('new_id', sa.Uuid(), nullable=True))
    op.add_column('transaction', sa.Column('new_sender_id', sa.Uuid(), nullable=True))
    op.add_column('transaction', sa.Column('new_receiver_id', sa.Uuid(), nullable=True))
    op.add_column('fraudalert', sa.Column('new_id', sa.Uuid(), nullable=True))
    op.add_column('fraudalert', sa.Column('new_user_id', sa.Uuid(), nullable=True))
    
    # Generate UUIDs for existing records
    op.execute("UPDATE \"user\" SET new_id = uuid_generate_v4()")
    op.execute("UPDATE transaction SET new_id = uuid_generate_v4()")
    op.execute("UPDATE fraudalert SET new_id = uuid_generate_v4()")
    
    # Create mapping between old and new IDs for foreign keys
    op.execute("""
        UPDATE transaction 
        SET new_sender_id = u.new_id 
        FROM \"user\" u 
        WHERE transaction.sender_id = u.id
    """)
    
    op.execute("""
        UPDATE transaction 
        SET new_receiver_id = u.new_id 
        FROM \"user\" u 
        WHERE transaction.receiver_id = u.id
    """)
    
    op.execute("""
        UPDATE fraudalert 
        SET new_user_id = u.new_id 
        FROM \"user\" u 
        WHERE fraudalert.user_id = u.id
    """)
    
    # Drop old columns and sequences
    op.drop_column('user', 'id')
    op.drop_column('transaction', 'id')
    op.drop_column('transaction', 'sender_id')
    op.drop_column('transaction', 'receiver_id')
    op.drop_column('fraudalert', 'id')
    op.drop_column('fraudalert', 'user_id')
    
    # Rename new columns to original names
    op.alter_column('user', 'new_id', new_column_name='id')
    op.alter_column('transaction', 'new_id', new_column_name='id')
    op.alter_column('transaction', 'new_sender_id', new_column_name='sender_id')
    op.alter_column('transaction', 'new_receiver_id', new_column_name='receiver_id')
    op.alter_column('fraudalert', 'new_id', new_column_name='id')
    op.alter_column('fraudalert', 'new_user_id', new_column_name='user_id')
    
    # Make UUID columns non-nullable and set as primary keys
    op.alter_column('user', 'id', nullable=False)
    op.alter_column('transaction', 'id', nullable=False)
    op.alter_column('transaction', 'sender_id', nullable=False)
    op.alter_column('transaction', 'receiver_id', nullable=False)
    op.alter_column('fraudalert', 'id', nullable=False)
    op.alter_column('fraudalert', 'user_id', nullable=False)
    
    # Add primary key constraints
    op.create_primary_key('user_pkey', 'user', ['id'])
    op.create_primary_key('transaction_pkey', 'transaction', ['id'])
    op.create_primary_key('fraudalert_pkey', 'fraudalert', ['id'])
    
    # Recreate foreign key constraints
    op.create_foreign_key('transaction_sender_id_fkey', 'transaction', 'user', ['sender_id'], ['id'])
    op.create_foreign_key('transaction_receiver_id_fkey', 'transaction', 'user', ['receiver_id'], ['id'])
    op.create_foreign_key('fraudalert_user_id_fkey', 'fraudalert', 'user', ['user_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema back to integers."""
    # Drop foreign key constraints
    op.drop_constraint('transaction_sender_id_fkey', 'transaction', type_='foreignkey')
    op.drop_constraint('transaction_receiver_id_fkey', 'transaction', type_='foreignkey') 
    op.drop_constraint('fraudalert_user_id_fkey', 'fraudalert', type_='foreignkey')
    
    # Drop primary key constraints
    op.drop_constraint('user_pkey', 'user', type_='primary')
    op.drop_constraint('transaction_pkey', 'transaction', type_='primary')
    op.drop_constraint('fraudalert_pkey', 'fraudalert', type_='primary')
    
    # Add new integer columns
    op.add_column('user', sa.Column('new_id', sa.INTEGER(), nullable=True))
    op.add_column('transaction', sa.Column('new_id', sa.INTEGER(), nullable=True))
    op.add_column('transaction', sa.Column('new_sender_id', sa.INTEGER(), nullable=True))
    op.add_column('transaction', sa.Column('new_receiver_id', sa.INTEGER(), nullable=True))
    op.add_column('fraudalert', sa.Column('new_id', sa.INTEGER(), nullable=True))
    op.add_column('fraudalert', sa.Column('new_user_id', sa.INTEGER(), nullable=True))
    
    # This is a destructive downgrade - we'll lose the UUID mapping
    # Generate sequential IDs for existing records
    op.execute("UPDATE \"user\" SET new_id = ROW_NUMBER() OVER (ORDER BY id)")
    op.execute("UPDATE transaction SET new_id = ROW_NUMBER() OVER (ORDER BY id)")
    op.execute("UPDATE fraudalert SET new_id = ROW_NUMBER() OVER (ORDER BY id)")
    
    # Note: This will break foreign key relationships as we can't map UUIDs back to the original integers
    op.execute("UPDATE transaction SET new_sender_id = 1, new_receiver_id = 1")
    op.execute("UPDATE fraudalert SET new_user_id = 1")
    
    # Drop old UUID columns
    op.drop_column('user', 'id')
    op.drop_column('transaction', 'id')
    op.drop_column('transaction', 'sender_id')
    op.drop_column('transaction', 'receiver_id')
    op.drop_column('fraudalert', 'id')
    op.drop_column('fraudalert', 'user_id')
    
    # Rename new columns
    op.alter_column('user', 'new_id', new_column_name='id')
    op.alter_column('transaction', 'new_id', new_column_name='id')
    op.alter_column('transaction', 'new_sender_id', new_column_name='sender_id')
    op.alter_column('transaction', 'new_receiver_id', new_column_name='receiver_id')
    op.alter_column('fraudalert', 'new_id', new_column_name='id')
    op.alter_column('fraudalert', 'new_user_id', new_column_name='user_id')
    
    # Make columns non-nullable and add constraints
    op.alter_column('user', 'id', nullable=False)
    op.alter_column('transaction', 'id', nullable=False)
    op.alter_column('transaction', 'sender_id', nullable=False)
    op.alter_column('transaction', 'receiver_id', nullable=False)
    op.alter_column('fraudalert', 'id', nullable=False)
    op.alter_column('fraudalert', 'user_id', nullable=False)
    
    # Add back primary keys with sequences
    op.create_primary_key('user_pkey', 'user', ['id'])
    op.create_primary_key('transaction_pkey', 'transaction', ['id'])
    op.create_primary_key('fraudalert_pkey', 'fraudalert', ['id'])
    
    # Recreate sequences
    op.execute("CREATE SEQUENCE user_id_seq OWNED BY \"user\".id")
    op.execute("CREATE SEQUENCE transaction_id_seq OWNED BY transaction.id")
    op.execute("CREATE SEQUENCE fraudalert_id_seq OWNED BY fraudalert.id")
    
    # Set sequence values
    op.execute("SELECT setval('user_id_seq', COALESCE((SELECT MAX(id) FROM \"user\"), 1))")
    op.execute("SELECT setval('transaction_id_seq', COALESCE((SELECT MAX(id) FROM transaction), 1))")
    op.execute("SELECT setval('fraudalert_id_seq', COALESCE((SELECT MAX(id) FROM fraudalert), 1))")
    
    # Set default values
    op.alter_column('user', 'id', server_default=sa.text("nextval('user_id_seq'::regclass)"))
    
    # Recreate foreign keys
    op.create_foreign_key('transaction_sender_id_fkey', 'transaction', 'user', ['sender_id'], ['id'])
    op.create_foreign_key('transaction_receiver_id_fkey', 'transaction', 'user', ['receiver_id'], ['id'])
    op.create_foreign_key('fraudalert_user_id_fkey', 'fraudalert', 'user', ['user_id'], ['id'])
