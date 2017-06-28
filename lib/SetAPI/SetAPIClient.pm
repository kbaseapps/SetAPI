package SetAPI::SetAPIClient;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

SetAPI::SetAPIClient

=head1 DESCRIPTION





=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => SetAPI::SetAPIClient::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my %arg_hash2 = @args;
	if (exists $arg_hash2{"token"}) {
	    $self->{token} = $arg_hash2{"token"};
	} elsif (exists $arg_hash2{"user_id"}) {
	    my $token = Bio::KBase::AuthToken->new(@args);
	    if (!$token->error_message) {
	        $self->{token} = $token->token;
	    }
	}
	
	if (exists $self->{token})
	{
	    $self->{client}->{token} = $self->{token};
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 get_expression_set_v1

  $return = $obj->get_expression_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.GetExpressionSetV1Params
$return is a SetAPI.GetExpressionSetV1Result
GetExpressionSetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetExpressionSetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.ExpressionSet
	info has a value which is a Workspace.object_info
ExpressionSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ExpressionSetItem
ExpressionSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_expression_id
	label has a value which is a string
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
	info has a value which is a Workspace.object_info
ws_expression_id is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string

</pre>

=end html

=begin text

$params is a SetAPI.GetExpressionSetV1Params
$return is a SetAPI.GetExpressionSetV1Result
GetExpressionSetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetExpressionSetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.ExpressionSet
	info has a value which is a Workspace.object_info
ExpressionSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ExpressionSetItem
ExpressionSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_expression_id
	label has a value which is a string
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
	info has a value which is a Workspace.object_info
ws_expression_id is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string


=end text

=item Description



=back

=cut

 sub get_expression_set_v1
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_expression_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_expression_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_expression_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.get_expression_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_expression_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_expression_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_expression_set_v1',
				       );
    }
}
 


=head2 save_expression_set_v1

  $result = $obj->save_expression_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.SaveExpressionSetV1Params
$result is a SetAPI.SaveExpressionSetV1Result
SaveExpressionSetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.ExpressionSet
ExpressionSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ExpressionSetItem
ExpressionSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_expression_id
	label has a value which is a string
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
	info has a value which is a Workspace.object_info
ws_expression_id is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SaveExpressionSetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

$params is a SetAPI.SaveExpressionSetV1Params
$result is a SetAPI.SaveExpressionSetV1Result
SaveExpressionSetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.ExpressionSet
ExpressionSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ExpressionSetItem
ExpressionSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_expression_id
	label has a value which is a string
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
	info has a value which is a Workspace.object_info
ws_expression_id is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SaveExpressionSetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info


=end text

=item Description



=back

=cut

 sub save_expression_set_v1
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function save_expression_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to save_expression_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'save_expression_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.save_expression_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'save_expression_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method save_expression_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'save_expression_set_v1',
				       );
    }
}
 


=head2 get_reads_alignment_set_v1

  $return = $obj->get_reads_alignment_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.GetReadsAlignmentSetV1Params
$return is a SetAPI.GetReadsAlignmentSetV1Result
GetReadsAlignmentSetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetReadsAlignmentSetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.ReadsAlignmentSet
	info has a value which is a Workspace.object_info
ReadsAlignmentSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ReadsAlignmentSetItem
ReadsAlignmentSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_reads_align_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
ws_reads_align_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string

</pre>

=end html

=begin text

$params is a SetAPI.GetReadsAlignmentSetV1Params
$return is a SetAPI.GetReadsAlignmentSetV1Result
GetReadsAlignmentSetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetReadsAlignmentSetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.ReadsAlignmentSet
	info has a value which is a Workspace.object_info
ReadsAlignmentSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ReadsAlignmentSetItem
ReadsAlignmentSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_reads_align_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
ws_reads_align_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string


=end text

=item Description



=back

=cut

 sub get_reads_alignment_set_v1
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_reads_alignment_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_reads_alignment_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_reads_alignment_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.get_reads_alignment_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_reads_alignment_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_reads_alignment_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_reads_alignment_set_v1',
				       );
    }
}
 


=head2 save_reads_alignment_set_v1

  $result = $obj->save_reads_alignment_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.SaveReadsAlignmentSetV1Params
$result is a SetAPI.SaveReadsAlignmentSetV1Result
SaveReadsAlignmentSetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.ReadsAlignmentSet
ReadsAlignmentSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ReadsAlignmentSetItem
ReadsAlignmentSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_reads_align_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
ws_reads_align_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
SaveReadsAlignmentSetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

$params is a SetAPI.SaveReadsAlignmentSetV1Params
$result is a SetAPI.SaveReadsAlignmentSetV1Result
SaveReadsAlignmentSetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.ReadsAlignmentSet
ReadsAlignmentSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ReadsAlignmentSetItem
ReadsAlignmentSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_reads_align_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
ws_reads_align_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
SaveReadsAlignmentSetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info


=end text

=item Description



=back

=cut

 sub save_reads_alignment_set_v1
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function save_reads_alignment_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to save_reads_alignment_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'save_reads_alignment_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.save_reads_alignment_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'save_reads_alignment_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method save_reads_alignment_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'save_reads_alignment_set_v1',
				       );
    }
}
 


=head2 get_reads_set_v1

  $result = $obj->get_reads_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.GetReadsSetV1Params
$result is a SetAPI.GetReadsSetV1Result
GetReadsSetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetReadsSetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.ReadsSet
	info has a value which is a Workspace.object_info
ReadsSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ReadsSetItem
ReadsSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_reads_id
	label has a value which is a string
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
	info has a value which is a Workspace.object_info
ws_reads_id is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string

</pre>

=end html

=begin text

$params is a SetAPI.GetReadsSetV1Params
$result is a SetAPI.GetReadsSetV1Result
GetReadsSetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetReadsSetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.ReadsSet
	info has a value which is a Workspace.object_info
ReadsSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ReadsSetItem
ReadsSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_reads_id
	label has a value which is a string
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
	info has a value which is a Workspace.object_info
ws_reads_id is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string


=end text

=item Description



=back

=cut

 sub get_reads_set_v1
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_reads_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_reads_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_reads_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.get_reads_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_reads_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_reads_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_reads_set_v1',
				       );
    }
}
 


=head2 save_reads_set_v1

  $result = $obj->save_reads_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.SaveReadsSetV1Params
$result is a SetAPI.SaveReadsSetV1Result
SaveReadsSetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.ReadsSet
ReadsSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ReadsSetItem
ReadsSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_reads_id
	label has a value which is a string
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
	info has a value which is a Workspace.object_info
ws_reads_id is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SaveReadsSetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

$params is a SetAPI.SaveReadsSetV1Params
$result is a SetAPI.SaveReadsSetV1Result
SaveReadsSetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.ReadsSet
ReadsSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.ReadsSetItem
ReadsSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_reads_id
	label has a value which is a string
	data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
	info has a value which is a Workspace.object_info
ws_reads_id is a string
DataAttachment is a reference to a hash where the following keys are defined:
	name has a value which is a string
	ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SaveReadsSetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info


=end text

=item Description



=back

=cut

 sub save_reads_set_v1
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function save_reads_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to save_reads_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'save_reads_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.save_reads_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'save_reads_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method save_reads_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'save_reads_set_v1',
				       );
    }
}
 


=head2 get_assembly_set_v1

  $result = $obj->get_assembly_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.GetAssemblySetV1Params
$result is a SetAPI.GetAssemblySetV1Result
GetAssemblySetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetAssemblySetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.AssemblySet
	info has a value which is a Workspace.object_info
AssemblySet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.AssemblySetItem
AssemblySetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_assembly_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
ws_assembly_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string

</pre>

=end html

=begin text

$params is a SetAPI.GetAssemblySetV1Params
$result is a SetAPI.GetAssemblySetV1Result
GetAssemblySetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetAssemblySetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.AssemblySet
	info has a value which is a Workspace.object_info
AssemblySet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.AssemblySetItem
AssemblySetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_assembly_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
ws_assembly_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string


=end text

=item Description



=back

=cut

 sub get_assembly_set_v1
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_assembly_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_assembly_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_assembly_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.get_assembly_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_assembly_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_assembly_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_assembly_set_v1',
				       );
    }
}
 


=head2 save_assembly_set_v1

  $result = $obj->save_assembly_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.SaveAssemblySetV1Params
$result is a SetAPI.SaveAssemblySetV1Result
SaveAssemblySetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.AssemblySet
AssemblySet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.AssemblySetItem
AssemblySetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_assembly_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
ws_assembly_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SaveAssemblySetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

$params is a SetAPI.SaveAssemblySetV1Params
$result is a SetAPI.SaveAssemblySetV1Result
SaveAssemblySetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.AssemblySet
AssemblySet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.AssemblySetItem
AssemblySetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_assembly_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
ws_assembly_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SaveAssemblySetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info


=end text

=item Description



=back

=cut

 sub save_assembly_set_v1
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function save_assembly_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to save_assembly_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'save_assembly_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.save_assembly_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'save_assembly_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method save_assembly_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'save_assembly_set_v1',
				       );
    }
}
 


=head2 get_genome_set_v1

  $result = $obj->get_genome_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.GetGenomeSetV1Params
$result is a SetAPI.GetGenomeSetV1Result
GetGenomeSetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetGenomeSetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.GenomeSet
	info has a value which is a Workspace.object_info
GenomeSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.GenomeSetItem
GenomeSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_genome_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
ws_genome_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string

</pre>

=end html

=begin text

$params is a SetAPI.GetGenomeSetV1Params
$result is a SetAPI.GetGenomeSetV1Result
GetGenomeSetV1Params is a reference to a hash where the following keys are defined:
	ref has a value which is a string
	include_item_info has a value which is a SetAPI.boolean
	ref_path_to_set has a value which is a reference to a list where each element is a string
boolean is an int
GetGenomeSetV1Result is a reference to a hash where the following keys are defined:
	data has a value which is a SetAPI.GenomeSet
	info has a value which is a Workspace.object_info
GenomeSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.GenomeSetItem
GenomeSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_genome_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
ws_genome_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string


=end text

=item Description



=back

=cut

 sub get_genome_set_v1
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_genome_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_genome_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_genome_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.get_genome_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_genome_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_genome_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_genome_set_v1',
				       );
    }
}
 


=head2 save_genome_set_v1

  $result = $obj->save_genome_set_v1($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.SaveGenomeSetV1Params
$result is a SetAPI.SaveGenomeSetV1Result
SaveGenomeSetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.GenomeSet
GenomeSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.GenomeSetItem
GenomeSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_genome_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
ws_genome_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SaveGenomeSetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

$params is a SetAPI.SaveGenomeSetV1Params
$result is a SetAPI.SaveGenomeSetV1Result
SaveGenomeSetV1Params is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	output_object_name has a value which is a string
	data has a value which is a SetAPI.GenomeSet
GenomeSet is a reference to a hash where the following keys are defined:
	description has a value which is a string
	items has a value which is a reference to a list where each element is a SetAPI.GenomeSetItem
GenomeSetItem is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_genome_id
	label has a value which is a string
	info has a value which is a Workspace.object_info
ws_genome_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SaveGenomeSetV1Result is a reference to a hash where the following keys are defined:
	set_ref has a value which is a string
	set_info has a value which is a Workspace.object_info


=end text

=item Description



=back

=cut

 sub save_genome_set_v1
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function save_genome_set_v1 (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to save_genome_set_v1:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'save_genome_set_v1');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.save_genome_set_v1",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'save_genome_set_v1',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method save_genome_set_v1",
					    status_line => $self->{client}->status_line,
					    method_name => 'save_genome_set_v1',
				       );
    }
}
 


=head2 list_sets

  $result = $obj->list_sets($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.ListSetParams
$result is a SetAPI.ListSetResult
ListSetParams is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	workspaces has a value which is a string
	include_set_item_info has a value which is a SetAPI.boolean
	include_metadata has a value which is a SetAPI.boolean
	include_raw_data_palettes has a value which is a SetAPI.boolean
boolean is an int
ListSetResult is a reference to a hash where the following keys are defined:
	sets has a value which is a reference to a list where each element is a SetAPI.SetInfo
	raw_data_palettes has a value which is a reference to a list where each element is a DataPaletteService.DataInfo
	raw_data_palette_refs has a value which is a reference to a hash where the key is a string and the value is a string
SetInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	info has a value which is a Workspace.object_info
	items has a value which is a reference to a list where each element is a SetAPI.SetItemInfo
	dp_ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SetItemInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	info has a value which is a Workspace.object_info
DataInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a DataPaletteService.ws_ref
	info has a value which is a Workspace.object_info
ws_ref is a string

</pre>

=end html

=begin text

$params is a SetAPI.ListSetParams
$result is a SetAPI.ListSetResult
ListSetParams is a reference to a hash where the following keys are defined:
	workspace has a value which is a string
	workspaces has a value which is a string
	include_set_item_info has a value which is a SetAPI.boolean
	include_metadata has a value which is a SetAPI.boolean
	include_raw_data_palettes has a value which is a SetAPI.boolean
boolean is an int
ListSetResult is a reference to a hash where the following keys are defined:
	sets has a value which is a reference to a list where each element is a SetAPI.SetInfo
	raw_data_palettes has a value which is a reference to a list where each element is a DataPaletteService.DataInfo
	raw_data_palette_refs has a value which is a reference to a hash where the key is a string and the value is a string
SetInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	info has a value which is a Workspace.object_info
	items has a value which is a reference to a list where each element is a SetAPI.SetItemInfo
	dp_ref has a value which is a SetAPI.ws_obj_id
ws_obj_id is a string
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SetItemInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	info has a value which is a Workspace.object_info
DataInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a DataPaletteService.ws_ref
	info has a value which is a Workspace.object_info
ws_ref is a string


=end text

=item Description

Use to get the top-level sets in a WS. Optionally can include
one level down members of those sets.
NOTE: DOES NOT PRESERVE ORDERING OF ITEM LIST IN DATA

=back

=cut

 sub list_sets
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_sets (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_sets:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_sets');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.list_sets",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_sets',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_sets",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_sets',
				       );
    }
}
 


=head2 get_set_items

  $result = $obj->get_set_items($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a SetAPI.GetSetItemsParams
$result is a SetAPI.GetSetItemsResult
GetSetItemsParams is a reference to a hash where the following keys are defined:
	set_refs has a value which is a reference to a list where each element is a SetAPI.SetReference
SetReference is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	path_to_set has a value which is a reference to a list where each element is a SetAPI.ws_obj_id
ws_obj_id is a string
GetSetItemsResult is a reference to a hash where the following keys are defined:
	sets has a value which is a reference to a list where each element is a SetAPI.SetInfo
SetInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	info has a value which is a Workspace.object_info
	items has a value which is a reference to a list where each element is a SetAPI.SetItemInfo
	dp_ref has a value which is a SetAPI.ws_obj_id
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SetItemInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

$params is a SetAPI.GetSetItemsParams
$result is a SetAPI.GetSetItemsResult
GetSetItemsParams is a reference to a hash where the following keys are defined:
	set_refs has a value which is a reference to a list where each element is a SetAPI.SetReference
SetReference is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	path_to_set has a value which is a reference to a list where each element is a SetAPI.ws_obj_id
ws_obj_id is a string
GetSetItemsResult is a reference to a hash where the following keys are defined:
	sets has a value which is a reference to a list where each element is a SetAPI.SetInfo
SetInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	info has a value which is a Workspace.object_info
	items has a value which is a reference to a list where each element is a SetAPI.SetItemInfo
	dp_ref has a value which is a SetAPI.ws_obj_id
object_info is a reference to a list containing 11 items:
	0: (objid) a Workspace.obj_id
	1: (name) a Workspace.obj_name
	2: (type) a Workspace.type_string
	3: (save_date) a Workspace.timestamp
	4: (version) an int
	5: (saved_by) a Workspace.username
	6: (wsid) a Workspace.ws_id
	7: (workspace) a Workspace.ws_name
	8: (chsum) a string
	9: (size) an int
	10: (meta) a Workspace.usermeta
obj_id is an int
obj_name is a string
type_string is a string
timestamp is a string
username is a string
ws_id is an int
ws_name is a string
usermeta is a reference to a hash where the key is a string and the value is a string
SetItemInfo is a reference to a hash where the following keys are defined:
	ref has a value which is a SetAPI.ws_obj_id
	info has a value which is a Workspace.object_info


=end text

=item Description

Use to drill down into one or more sets, the position in the
return 'sets' list will match the position in the input ref list.
NOTE: DOES NOT PRESERVE ORDERING OF ITEM LIST IN DATA

=back

=cut

 sub get_set_items
{
    my($self, @args) = @_;

# Authentication: optional

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_set_items (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_set_items:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_set_items');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "SetAPI.get_set_items",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_set_items',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_set_items",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_set_items',
				       );
    }
}
 
  
sub status
{
    my($self, @args) = @_;
    if ((my $n = @args) != 0) {
        Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
                                   "Invalid argument count for function status (received $n, expecting 0)");
    }
    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
        method => "SetAPI.status",
        params => \@args,
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
                           code => $result->content->{error}->{code},
                           method_name => 'status',
                           data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
                          );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method status",
                        status_line => $self->{client}->status_line,
                        method_name => 'status',
                       );
    }
}
   

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "SetAPI.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'get_set_items',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method get_set_items",
            status_line => $self->{client}->status_line,
            method_name => 'get_set_items',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for SetAPI::SetAPIClient\n";
    }
    if ($sMajor == 0) {
        warn "SetAPI::SetAPIClient version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 boolean

=over 4



=item Description

A boolean. 0 = false, 1 = true.


=item Definition

=begin html

<pre>
an int
</pre>

=end html

=begin text

an int

=end text

=back



=head2 ws_obj_id

=over 4



=item Description

The workspace ID for a any data object.
@id ws


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 DataAttachment

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
name has a value which is a string
ref has a value which is a SetAPI.ws_obj_id

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
name has a value which is a string
ref has a value which is a SetAPI.ws_obj_id


=end text

=back



=head2 ws_expression_id

=over 4



=item Description

The workspace id for a ReadsAlignment data object.
@id ws KBaseRNASeq.RNASeqExpression


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 ExpressionSetItem

=over 4



=item Description

When saving a ExpressionSet, only 'ref' is required.
You should never set 'info'.  'info' is provided optionally when fetching
the ExpressionSet.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_expression_id
label has a value which is a string
data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_expression_id
label has a value which is a string
data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
info has a value which is a Workspace.object_info


=end text

=back



=head2 ExpressionSet

=over 4



=item Description

When building a ExpressionSet, all Expression objects must be aligned against the same
genome. This is not part of the object type, but enforced during a call to
save_expression_set_v1.
@meta ws description as description
@meta ws length(items) as item_count


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.ExpressionSetItem

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.ExpressionSetItem


=end text

=back



=head2 GetExpressionSetV1Params

=over 4



=item Description

ref - workspace reference to ExpressionSet object.
include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                    metadata) for each Expression object in the Set


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string


=end text

=back



=head2 GetExpressionSetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.ExpressionSet
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.ExpressionSet
info has a value which is a Workspace.object_info


=end text

=back



=head2 SaveExpressionSetV1Params

=over 4



=item Description

workspace_name or workspace_id - alternative options defining
    target workspace,
output_object_name - workspace object name (this parameter is
    used together with one of workspace params from above)


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.ExpressionSet

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.ExpressionSet


=end text

=back



=head2 SaveExpressionSetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info


=end text

=back



=head2 ws_reads_align_id

=over 4



=item Description

The workspace id for a ReadsAlignment data object.
@id ws KBaseRNASeq.RNASeqAlignment


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 ReadsAlignmentSetItem

=over 4



=item Description

When saving a ReadsAlignmentSet, only 'ref' is required.
You should never set 'info'.  'info' is provided optionally when fetching
the ReadsAlignmentSet.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_reads_align_id
label has a value which is a string
info has a value which is a Workspace.object_info
data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_reads_align_id
label has a value which is a string
info has a value which is a Workspace.object_info
data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment


=end text

=back



=head2 ReadsAlignmentSet

=over 4



=item Description

When building a ReadsAlignmentSet, all ReadsAlignments must be aligned against the same
genome. This is not part of the object type, but enforced during a call to
save_reads_alignment_set_v1.
@meta ws description as description
@meta ws length(items) as item_count


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.ReadsAlignmentSetItem

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.ReadsAlignmentSetItem


=end text

=back



=head2 GetReadsAlignmentSetV1Params

=over 4



=item Description

ref - workspace reference to ReadsAlignmentSet object.
include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                    metadata) for each ReadsAlignment object in the Set


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string


=end text

=back



=head2 GetReadsAlignmentSetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.ReadsAlignmentSet
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.ReadsAlignmentSet
info has a value which is a Workspace.object_info


=end text

=back



=head2 SaveReadsAlignmentSetV1Params

=over 4



=item Description

workspace_name or workspace_id - alternative options defining
    target workspace,
output_object_name - workspace object name (this parameter is
    used together with one of workspace params from above)


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.ReadsAlignmentSet

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.ReadsAlignmentSet


=end text

=back



=head2 SaveReadsAlignmentSetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info


=end text

=back



=head2 ws_reads_id

=over 4



=item Description

The workspace ID for a Reads data object.
@id ws KBaseFile.PairedEndLibrary KBaseFile.SingleEndLibrary


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 ReadsSetItem

=over 4



=item Description

When saving a ReadsSet, only 'ref' is required.  You should
never set 'info'.  'info' is provided optionally when fetching
the ReadsSet.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_reads_id
label has a value which is a string
data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_reads_id
label has a value which is a string
data_attachments has a value which is a reference to a list where each element is a SetAPI.DataAttachment
info has a value which is a Workspace.object_info


=end text

=back



=head2 ReadsSet

=over 4



=item Description

@meta ws description as description
@meta ws length(items) as item_count


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.ReadsSetItem

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.ReadsSetItem


=end text

=back



=head2 GetReadsSetV1Params

=over 4



=item Description

ref - workspace reference to ReadsGroup object.
include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                    metadata) for each Reads object in the Set


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string


=end text

=back



=head2 GetReadsSetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.ReadsSet
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.ReadsSet
info has a value which is a Workspace.object_info


=end text

=back



=head2 SaveReadsSetV1Params

=over 4



=item Description

workspace_name or workspace_id - alternative options defining
    target workspace,
output_object_name - workspace object name (this parameter is
    used together with one of workspace params from above)


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.ReadsSet

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.ReadsSet


=end text

=back



=head2 SaveReadsSetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info


=end text

=back



=head2 ws_assembly_id

=over 4



=item Description

The workspace ID for an Assembly object.
@id ws KBaseGenomeAnnotations.Assembly


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 AssemblySetItem

=over 4



=item Description

When saving an AssemblySet, only 'ref' is required.
You should never set 'info'.  'info' is provided optionally when fetching
the AssemblySet.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_assembly_id
label has a value which is a string
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_assembly_id
label has a value which is a string
info has a value which is a Workspace.object_info


=end text

=back



=head2 AssemblySet

=over 4



=item Description

@meta ws description as description
@meta ws length(items) as item_count


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.AssemblySetItem

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.AssemblySetItem


=end text

=back



=head2 GetAssemblySetV1Params

=over 4



=item Description

ref - workspace reference to AssemblyGroup object.
include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                    metadata) for each Assembly object in the Set


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string


=end text

=back



=head2 GetAssemblySetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.AssemblySet
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.AssemblySet
info has a value which is a Workspace.object_info


=end text

=back



=head2 SaveAssemblySetV1Params

=over 4



=item Description

workspace_name or workspace_id - alternative options defining
    target workspace,
output_object_name - workspace object name (this parameter is
    used together with one of workspace params from above)


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.AssemblySet

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.AssemblySet


=end text

=back



=head2 SaveAssemblySetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info


=end text

=back



=head2 ws_genome_id

=over 4



=item Description

The workspace ID for a Genome object.
@id ws KBaseGenomes.Genome


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 GenomeSetItem

=over 4



=item Description

When saving an GenomeSet, only 'ref' is required.
You should never set 'info'.  'info' is provided optionally when fetching
the GenomeSet.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_genome_id
label has a value which is a string
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_genome_id
label has a value which is a string
info has a value which is a Workspace.object_info


=end text

=back



=head2 GenomeSet

=over 4



=item Description

@meta ws description as description
@meta ws length(items) as item_count


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.GenomeSetItem

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
description has a value which is a string
items has a value which is a reference to a list where each element is a SetAPI.GenomeSetItem


=end text

=back



=head2 GetGenomeSetV1Params

=over 4



=item Description

ref - workspace reference to GenomeGroup object.
include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                    metadata) for each Genome object in the Set


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a string
include_item_info has a value which is a SetAPI.boolean
ref_path_to_set has a value which is a reference to a list where each element is a string


=end text

=back



=head2 GetGenomeSetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.GenomeSet
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
data has a value which is a SetAPI.GenomeSet
info has a value which is a Workspace.object_info


=end text

=back



=head2 SaveGenomeSetV1Params

=over 4



=item Description

workspace_name or workspace_id - alternative options defining
    target workspace,
output_object_name - workspace object name (this parameter is
    used together with one of workspace params from above)


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.GenomeSet

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace has a value which is a string
output_object_name has a value which is a string
data has a value which is a SetAPI.GenomeSet


=end text

=back



=head2 SaveGenomeSetV1Result

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
set_ref has a value which is a string
set_info has a value which is a Workspace.object_info


=end text

=back



=head2 ListSetParams

=over 4



=item Description

workspace - workspace name or ID (alternative to
    workspaces parameter),
workspaces - list of workspace name ot ID (alternative to
    workspace parameter),
include_metadata - flag for including metadata into Set object info
    and into object info of items (it affects DP raw data as well),
include_raw_data_palettes - advanced option designed for
    optimization of listing methods in NarrativeService.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace has a value which is a string
workspaces has a value which is a string
include_set_item_info has a value which is a SetAPI.boolean
include_metadata has a value which is a SetAPI.boolean
include_raw_data_palettes has a value which is a SetAPI.boolean

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace has a value which is a string
workspaces has a value which is a string
include_set_item_info has a value which is a SetAPI.boolean
include_metadata has a value which is a SetAPI.boolean
include_raw_data_palettes has a value which is a SetAPI.boolean


=end text

=back



=head2 SetItemInfo

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_obj_id
info has a value which is a Workspace.object_info

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_obj_id
info has a value which is a Workspace.object_info


=end text

=back



=head2 SetInfo

=over 4



=item Description

dp_ref - optional reference to DataPalette container in case given set object
    is coming from DataPalette.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_obj_id
info has a value which is a Workspace.object_info
items has a value which is a reference to a list where each element is a SetAPI.SetItemInfo
dp_ref has a value which is a SetAPI.ws_obj_id

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_obj_id
info has a value which is a Workspace.object_info
items has a value which is a reference to a list where each element is a SetAPI.SetItemInfo
dp_ref has a value which is a SetAPI.ws_obj_id


=end text

=back



=head2 ListSetResult

=over 4



=item Description

raw_data_palettes - optional DP output turned on by 'include_raw_data_palettes'
    in input parameters,
raw_data_palette_refs - optional DP output (mapping from workspace Id to reference
    to DataPalette container existing in particular workspace) turned on by
    'include_raw_data_palettes' in input parameters,


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
sets has a value which is a reference to a list where each element is a SetAPI.SetInfo
raw_data_palettes has a value which is a reference to a list where each element is a DataPaletteService.DataInfo
raw_data_palette_refs has a value which is a reference to a hash where the key is a string and the value is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
sets has a value which is a reference to a list where each element is a SetAPI.SetInfo
raw_data_palettes has a value which is a reference to a list where each element is a DataPaletteService.DataInfo
raw_data_palette_refs has a value which is a reference to a hash where the key is a string and the value is a string


=end text

=back



=head2 SetReference

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_obj_id
path_to_set has a value which is a reference to a list where each element is a SetAPI.ws_obj_id

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
ref has a value which is a SetAPI.ws_obj_id
path_to_set has a value which is a reference to a list where each element is a SetAPI.ws_obj_id


=end text

=back



=head2 GetSetItemsParams

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
set_refs has a value which is a reference to a list where each element is a SetAPI.SetReference

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
set_refs has a value which is a reference to a list where each element is a SetAPI.SetReference


=end text

=back



=head2 GetSetItemsResult

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
sets has a value which is a reference to a list where each element is a SetAPI.SetInfo

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
sets has a value which is a reference to a list where each element is a SetAPI.SetInfo


=end text

=back



=cut

package SetAPI::SetAPIClient::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
