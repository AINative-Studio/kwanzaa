"""Initial schema with 6 core tables for Kwanzaa RAG system.

Revision ID: 001
Revises:
Create Date: 2026-01-16 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all core tables for Kwanzaa RAG system."""

    # Create sources table
    op.create_table(
        'sources',
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_name', sa.String(length=255), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('canonical_url', sa.String(length=500), nullable=False),
        sa.Column('license', sa.String(length=255), nullable=False),
        sa.Column('access_method', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('priority >= 0 AND priority <= 5', name='check_priority_range'),
        sa.CheckConstraint(
            "source_type IN ('government', 'press', 'archive', 'academic', 'museum', 'community', 'other')",
            name='check_source_type'
        ),
        sa.CheckConstraint(
            "access_method IN ('api', 'scrape', 'manual', 'download')",
            name='check_access_method'
        ),
        sa.PrimaryKeyConstraint('source_id')
    )
    op.create_index('ix_sources_source_name', 'sources', ['source_name'], unique=True)
    op.create_index('ix_sources_source_type', 'sources', ['source_type'], unique=False)
    op.create_index('ix_sources_created_at', 'sources', ['created_at'], unique=False)

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('canonical_url', sa.String(length=500), nullable=False),
        sa.Column('source_org', sa.String(length=255), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('license', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('full_text', sa.Text(), nullable=True),
        sa.Column('extra_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('year >= 1600 AND year <= 2100', name='check_year_range'),
        sa.CheckConstraint(
            "content_type IN ('speech', 'letter', 'document', 'article', 'book', 'interview', 'multimedia', 'other')",
            name='check_content_type'
        ),
        sa.ForeignKeyConstraint(['source_id'], ['sources.source_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('document_id')
    )
    op.create_index('ix_documents_source_id', 'documents', ['source_id'], unique=False)
    op.create_index('ix_documents_canonical_url', 'documents', ['canonical_url'], unique=True)
    op.create_index('ix_documents_source_org', 'documents', ['source_org'], unique=False)
    op.create_index('ix_documents_year', 'documents', ['year'], unique=False)
    op.create_index('ix_documents_content_type', 'documents', ['content_type'], unique=False)
    op.create_index('ix_documents_created_at', 'documents', ['created_at'], unique=False)
    op.create_index('idx_document_year_content', 'documents', ['year', 'content_type'], unique=False)

    # Create chunks table
    op.create_table(
        'chunks',
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('citation_label', sa.String(length=500), nullable=False),
        sa.Column('namespace', sa.String(length=100), nullable=False),
        sa.Column('vector_id', sa.String(length=255), nullable=True),
        sa.Column('retrieved_at', sa.DateTime(), nullable=True),
        sa.Column('provenance_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('chunk_index >= 0', name='check_chunk_index_positive'),
        sa.CheckConstraint(
            "namespace IN ('founding', 'core_texts', 'speeches', 'letters', 'multimedia', 'supplemental')",
            name='check_namespace'
        ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('chunk_id')
    )
    op.create_index('ix_chunks_document_id', 'chunks', ['document_id'], unique=False)
    op.create_index('ix_chunks_namespace', 'chunks', ['namespace'], unique=False)
    op.create_index('ix_chunks_vector_id', 'chunks', ['vector_id'], unique=False)
    op.create_index('ix_chunks_created_at', 'chunks', ['created_at'], unique=False)
    op.create_index('idx_chunk_document_index', 'chunks', ['document_id', 'chunk_index'], unique=True)
    op.create_index('idx_chunk_namespace_vector', 'chunks', ['namespace', 'vector_id'], unique=False)

    # Create collections table
    op.create_table(
        'collections',
        sa.Column('collection_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collection_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_threshold', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            'default_threshold IS NULL OR (default_threshold >= 0.0 AND default_threshold <= 1.0)',
            name='check_threshold_range'
        ),
        sa.PrimaryKeyConstraint('collection_id')
    )
    op.create_index('ix_collections_collection_name', 'collections', ['collection_name'], unique=True)
    op.create_index('ix_collections_created_at', 'collections', ['created_at'], unique=False)

    # Create ingestion_logs table
    op.create_table(
        'ingestion_logs',
        sa.Column('run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_name', sa.String(length=255), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('documents_processed', sa.Integer(), nullable=True),
        sa.Column('chunks_created', sa.Integer(), nullable=True),
        sa.Column('errors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('run_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint(
            "status IN ('running', 'completed', 'failed', 'partial')",
            name='check_status'
        ),
        sa.CheckConstraint(
            'documents_processed IS NULL OR documents_processed >= 0',
            name='check_documents_processed'
        ),
        sa.CheckConstraint(
            'chunks_created IS NULL OR chunks_created >= 0',
            name='check_chunks_created'
        ),
        sa.PrimaryKeyConstraint('run_id')
    )
    op.create_index('ix_ingestion_logs_source_name', 'ingestion_logs', ['source_name'], unique=False)
    op.create_index('ix_ingestion_logs_started_at', 'ingestion_logs', ['started_at'], unique=False)
    op.create_index('ix_ingestion_logs_status', 'ingestion_logs', ['status'], unique=False)
    op.create_index('idx_ingestion_source_status', 'ingestion_logs', ['source_name', 'status'], unique=False)
    op.create_index(
        'idx_ingestion_started',
        'ingestion_logs',
        [sa.text('started_at DESC')],
        unique=False,
        postgresql_using='btree'
    )

    # Create evaluations table
    op.create_table(
        'evaluations',
        sa.Column('eval_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('eval_type', sa.String(length=100), nullable=False),
        sa.Column('run_date', sa.DateTime(), nullable=False),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('test_cases', sa.Integer(), nullable=False),
        sa.Column('passed', sa.Integer(), nullable=False),
        sa.Column('failed', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('test_cases >= 0', name='check_test_cases'),
        sa.CheckConstraint('passed >= 0', name='check_passed'),
        sa.CheckConstraint('failed >= 0', name='check_failed'),
        sa.CheckConstraint('passed + failed <= test_cases', name='check_passed_failed_sum'),
        sa.CheckConstraint(
            "eval_type IN ('citation_coverage', 'refusal_accuracy', 'hallucination', 'retrieval_quality', 'answer_quality', 'other')",
            name='check_eval_type'
        ),
        sa.PrimaryKeyConstraint('eval_id')
    )
    op.create_index('ix_evaluations_eval_type', 'evaluations', ['eval_type'], unique=False)
    op.create_index('ix_evaluations_run_date', 'evaluations', ['run_date'], unique=False)
    op.create_index('idx_evaluation_type_date', 'evaluations', ['eval_type', 'run_date'], unique=False)


def downgrade() -> None:
    """Drop all core tables."""
    op.drop_table('evaluations')
    op.drop_table('ingestion_logs')
    op.drop_table('collections')
    op.drop_table('chunks')
    op.drop_table('documents')
    op.drop_table('sources')
