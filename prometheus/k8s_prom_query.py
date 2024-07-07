

class K8sPromQueryInstance:
    def __init__(self, cluster_info, access_point_id=None, component=None):
        self.tidb_instance_query = '''
            kube_node_labels{tenant="%s",label_cluster="%s",label_component="tidb"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'])

        self.tidb_instance_query_ac = '''
            kube_node_labels{tenant="%s",label_cluster="%s",label_component="tidb", label_tidbcloud_cluster="%s-%s"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'], cluster_info['cluster_id'], access_point_id)

        self.tidb_instance_query_ac_default = '''
            kube_node_labels{tenant="%s",label_cluster="%s",label_component="tidb", label_tidbcloud_cluster="%s"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'], cluster_info['cluster_id'])

        self.tikv_instance_query = '''
             kube_node_labels{tenant="%s",label_cluster="%s",label_component="tikv"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'])

        self.pd_instance_query = '''
             kube_node_labels{tenant="%s",label_cluster="%s",label_component="pd"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'])

        self.tiflash_instance_query = '''
             kube_node_labels{tenant="%s",label_cluster="%s",label_component="tiflash"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'])

        #self.component_query = 'sum(kube_node_labels{tenant="%s",label_tidbcloud_cluster="%s"}) by (label_component)' % (
        #cluster_info['tenant_id'], cluster_info['cluster_id'])
        self.component_query = 'sum(kube_node_labels{tenant="%s",label_tidb_namespace="tidb%s"}) by (label_component)' % (
        cluster_info['tenant_id'], cluster_info['cluster_id'])

        self.dedicated_cluster_by_tenant_query = 'kube_node_labels{tenant="%s",label_servicetype="dedicated"}' % (cluster_info['tenant_id'])

        self.dedicated_cluster_by_project_query = 'kube_node_labels{tenant="%s",project="%s",label_servicetype="dedicated"}' % (cluster_info['tenant_id'], cluster_info['project_id'])

        self.component_instance_query = '''
            kube_node_labels{tenant="%s",label_cluster="%s",label_component="%s"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'], component)


class K8sPromQueryInstanceMetrics:
    def __init__(self, cluster_info, instance_name):
        self.instance_disk_iops_query = '''
            sum(rate(node_disk_writes_completed_total{tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[2m])) by (instance) + 
            sum(rate(node_disk_reads_completed_total{tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[2m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name, cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name)

        self.instance_disk_bandwidth_query = '''
            sum(rate(node_disk_read_bytes_total{tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[2m])) by (instance) + 
            sum(rate(node_disk_written_bytes_total{tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[2m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name, cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name)

        self.instance_network_received_query = '''
            sum(rate(node_network_receive_bytes_total{job="node-exporter", tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[1m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name)

        self.instance_network_transmitted_query = '''
            sum(rate(node_network_transmit_bytes_total{job="node-exporter", tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[1m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name)


class K8sPromQueryBatchInstanceMetrics:
    def __init__(self, cluster_info, instances):
        self.batch_instance_disk_iops_query = '''
             sum(rate(node_disk_writes_completed_total{tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[2m])) by (instance) + 
             sum(rate(node_disk_reads_completed_total{tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[2m])) by (instance)
         ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances, cluster_info['tenant_id'],
                cluster_info['k8s_cluster'], instances)

        self.batch_instance_disk_bandwidth_query = '''
            sum(rate(node_disk_read_bytes_total{tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[2m])) by (instance) + 
            sum(rate(node_disk_written_bytes_total{tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[2m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances, cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances)

        self.batch_instance_network_received_query = '''
            sum(rate(node_network_receive_bytes_total{job="node-exporter", tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[1m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances)

        self.batch_instance_network_transmitted_query = '''
            sum(rate(node_network_transmit_bytes_total{job="node-exporter", tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[1m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances)


